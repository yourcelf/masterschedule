import json
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, Http404, HttpResponse
from django.contrib import messages
from vanilla import ListView, DetailView, UpdateView, CreateView

from schedule.models import *
from schedule.forms import *

class ConferenceList(ListView):
    model = Conference
    def get_queryset(self):
        return Conference.objects.order_by('-created')

class MasterSchedule(DetailView):
    model = Conference
    template_name = "schedule/master_schedule.html"

    def event_filter(self, qs):
        return qs

    def get_context_data(self, **kwargs):
        context = super(MasterSchedule, self).get_context_data(**kwargs)
        conference = context['conference']

        periods = list(Period.objects.filter(
                conference=conference
            ).order_by('start_date'))
        events = list(self.event_filter(Event.objects.filter(
                conference=conference
            )).select_related(
                'period'
            ).prefetch_related(
                'eventrole_set'
            ).order_by('start_date'))
        people = list(Person.objects.filter(
                conference=conference
            ).prefetch_related(
                'othercommitment_set',
                'eventrole_set'
            ).order_by('availability_start_date'))


        # Get a list of non-overlapping spans of time during which events or
        # periods occur.  To accomplish this, start with a discrete time series
        # in 5 minute chunks through each event.
        resolution = datetime.timedelta(seconds=5 * 60) # 15 minutes
        block_gap = datetime.timedelta(hours=1)
        time_series = set()
        for object_list in (events, periods):
            for obj in object_list:
                t = obj.start_date
                while t <= obj.end_date:
                    time_series.add(t)
                    t += resolution
        time_series = sorted(list(time_series))

        # Sort the time series into occupied chunks.
        if time_series:
            chunks = [{
                "start": time_series[0],
                "end": time_series[0],
                "periods": [],
                "events": [],
            }]
            for t in time_series:
                if t - chunks[-1]["end"] <= block_gap:
                    chunks[-1]["end"] = t
                else:
                    chunks.append({"start": t, "end": t, "events": [], "periods": []})
        else:
            chunks = []

        # Sort the objects into the chunks.
        for object_list, key in ((events, "events"), (periods, "periods")):
            for obj in object_list:
                for i, chunk in enumerate(chunks):
                    if (obj.start_date >= chunk["start"]) and (obj.end_date <= chunk["end"]):
                        chunk[key].append(obj)
                        break

        context.update({"chunks": chunks})
        return context

class PersonalSchedule(MasterSchedule):
    def get_object(self):
        self.person = get_object_or_404(Person, pk=self.kwargs['pk'])
        return self.person.conference

    def event_filter(self, qs):
        return qs.filter(eventrole__person=self.person).distinct()

    def get_context_data(self, **kwargs):
        context = super(PersonalSchedule, self).get_context_data(**kwargs)
        context['filter'] = "Schedule for {}".format(unicode(self.person))
        return context

class PersonList(CreateView):
    template_name = "schedule/person_list.html"
    form_class = PersonForm

    def get_context_data(self, **kwargs):
        context = super(PersonList, self).get_context_data(**kwargs)
        context['conference'] = get_object_or_404(Conference, pk=self.kwargs['pk'])
        context['object_list'] = context['conference'].person_set.all()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        person, created = Person.objects.get_or_create(
            conference=context['conference'],
            **form.cleaned_data
        )
        return redirect(self.request.path)

class EventAssigner(ListView):
    template_name = "schedule/event_assigner.html"
    def get_queryset(self):
        self.conference = get_object_or_404(Conference, pk=self.kwargs['pk'])
        return Event.objects.filter(
                conference__id=self.kwargs['pk']).order_by('start_date'
            ).prefetch_related('eventrole_set')

    def get_context_data(self, **kwargs):
        context = super(EventAssigner, self).get_context_data(**kwargs)
        _add_event_context(context, self.conference)
        return context

def _add_event_context(context, conference):
    context['conference'] = conference
    context['role_types'] = list(conference.roletype_set.all())
    context["venues"] = list(conference.venue_set.all())
    return context


def add_event_role(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")
    event = get_object_or_404(Event.objects.select_related('conference'),
                              pk=request.POST.get("eventId"))

    person_id = request.POST.get("person")
    if person_id:
        person = get_object_or_404(Person.objects.filter(conference=event.conference),
                pk=person_id)
    else:
        person = None

    roletype = get_object_or_404(RoleType.objects.filter(conference=event.conference),
            pk=request.POST.get("role"))

    eventrole_id = request.POST.get("eventRoleId")
    if eventrole_id:
        role = get_object_or_404(EventRole.objects.filter(event=event), pk=eventrole_id)
        role.person = person
        role.role = roletype
        role.save()
    else:
        role = EventRole.objects.get_or_create(
            event=event,
            person=person,
            role=roletype)[0]
    event.eventrole_set.add(role)
    context = {"event": event}
    _add_event_context(context, event.conference)
    return render(request, "schedule/_event_role_row.html", context)

def remove_event_role(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")
    role = get_object_or_404(EventRole, pk=request.POST.get("eventRoleId"))
    event = role.event
    role.delete()
    context = {"event": event}
    _add_event_context(context, event.conference)
    return render(request, "schedule/_event_role_row.html", context)

def update_event_attribute(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    event = get_object_or_404(Event, pk=request.POST.get("eventId"))
    name = request.POST.get("name")
    if name not in set(["venue_id"]):
        return HttpResponseBadRequest("Name not allowed.")
    setattr(event, request.POST.get("name"), request.POST.get("value") or None)
    event.save()
    context = {"event": event}
    _add_event_context(context, event.conference)
    return render(request, "schedule/_event_role_row.html", context)


def get_available_people(request):
    event = get_object_or_404(
            Event.objects.select_related('conference'),
            pk=request.GET.get('eventId'))
    role_type = get_object_or_404(RoleType, pk=request.GET.get("roleTypeId"))
    event_role_id = request.GET.get("eventRoleId", None)

    people = list(Person.objects.filter(conference=event.conference))
    people_ids = [p.id for p in people]
    preferences = set(RolePreference.objects.filter(person__in=people_ids,
        roletype=role_type).values_list('person_id', flat=True))
    other_commitments = set(OtherCommitment.objects.filter(person__in=people,
        start_date__lte=event.end_date, end_date__gte=event.start_date
    ).values_list('person_id', flat=True))
    
    conflicting_roles = {}
    qs = EventRole.objects.filter(
        event__start_date__lte=event.end_date,
        event__end_date__gte=event.start_date,
    ).select_related('role', 'event')
    if event_role_id is not None:
        qs = qs.exclude(id=event_role_id)
    for role in qs:
        conflicting_roles[role.person_id] = role

    results = []
    for person in people:
        has_submitted_availability = (
            person.availability_start_date is not None and
            person.availability_end_date is not None
        )
        has_other_commitment = person.id in other_commitments
        is_generally_available = (
            has_submitted_availability and
            person.availability_start_date < event.start_date and
            person.availability_end_date > event.end_date
        )
        has_other_assignment = person.id in conflicting_roles
        if has_other_assignment:
            other_assignment = {
                "role": unicode(conflicting_roles[person.id].role),
                "event": unicode(conflicting_roles[person.id].event)
            }
        else:
            other_assignment = None

        results.append({
            "id": person.id,
            "text": person.name,
            "preference": person.id in preferences,
            "attending": person.attending,
            "is_generally_available": is_generally_available,
            "has_submitted_availability": has_submitted_availability,
            "has_other_commitment": has_other_commitment,
            "has_other_assignment": has_other_assignment,
            "other_assignment": other_assignment,
            "available": (
                person.attending and
                is_generally_available and
                not has_other_commitment and
                not has_other_assignment
            ),
        })
    def sort(obj):
        return [
            obj["available"],
            obj["preference"],
            obj["attending"] and not obj["has_submitted_availability"],
            not (obj["has_other_commitment"] or obj["has_other_assignment"]),
        ]

    results.sort(key=sort, reverse=True)

    res = json.dumps({"more": False, "results": results})
    return HttpResponse(res, content_type="application/json")

class AvailabilitySurvey(UpdateView):
    model = Person
    form_class = AvailabilityForm
    template_name = "schedule/availability.html"

    def get_context_data(self, **kwargs):
        context = super(AvailabilitySurvey, self).get_context_data(**kwargs)
        person = context['object']
        context['othercommitment_formset'] = OtherCommitmentFormset(
                self.request.POST or None, instance=person)
        context['conference'] = person.conference
        roleprefs = set(person.rolepreference_set.all().values_list('roletype_id', flat=True))
        context['roleprefs'] = [(rt, rt.id in roleprefs) for rt in person.conference.roletype_set.all()]
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        othercommitment_formset = context['othercommitment_formset']
        if othercommitment_formset.is_valid():
            person = form.save()
            instances = othercommitment_formset.save()
            for rt, pref in context['roleprefs']:
                wants_pref = bool(self.request.POST.get("rolepref-{}".format(rt.pk)))
                if pref and not wants_pref:
                    RolePreference.objects.filter(person=person, roletype=rt).delete()
                if wants_pref and not pref:
                    RolePreference.objects.create(person=person, roletype=rt)
            messages.info(self.request, "Thank you! You can come back and change your responses if you need to.")
            return redirect(self.request.path)
        else:
            return self.render_to_response(context)
