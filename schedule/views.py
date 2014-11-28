import json
import datetime
from collections import defaultdict
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, Http404, HttpResponse, QueryDict
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from vanilla import ListView, DetailView, UpdateView, CreateView, GenericView
import vobject

from schedule.models import *
from schedule.forms import *

def auth_problems(user, conference=None):
    p = {}
    if not user.is_authenticated():
        p['not authenticated'] = True
    if conference and not conference.is_admin(user):
        p['not admin'] = True
    return p

def _admin_or_deny(user, conference):
    if auth_problems(user, conference):
        raise PermissionDenied

def _problem_response(request, problems):
    if 'not authenticated' in problems:
        messages.info(request, 
            "You must log in as an admin of this conference to assign "
            "roles.")
        return redirect("auth_login")
    elif 'not admin' in problems:
        messages.info(request, 
            "You must be an admin of this conference to assign roles. "
            "Please log in as an admin to continue.")
        return redirect("auth_login")
    elif problems:
        return HttpResponseBadRequest()

class ConferenceCreate(CreateView):
    model = Conference
    form_class = CreateConferenceForm

    def dispatch(self, request, *args, **kwargs):
        problems = auth_problems(request.user)
        if problems:
            return _problem_response(request, problems)
        return super(ConferenceCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(ConferenceCreate, self).get_context_data(*args, **kwargs)
        context['admins_json'] = json.dumps([{
            "id": self.request.user.id, "email": self.request.user.email, "exists": True
        }])
        return context

class ConferenceUpdate(UpdateView):
    model = Conference
    form_class = UpdateConferenceForm

    def dispatch(self, request, *args, **kwargs):
        self.conference = Conference.objects.prefetch_related(
                'admins', 'prospective_admins'
            ).get(random_slug=self.kwargs.get('slug'))
        problems = auth_problems(request.user, self.conference)
        if problems:
            return _problem_response(request, problems)
        return super(ConferenceUpdate, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.conference

    def get_context_data(self, *args, **kwargs):
        context = super(ConferenceUpdate, self).get_context_data(*args, **kwargs)
        context['conference'] = self.conference
        context["is_admin"] = self.conference.is_admin(self.request.user),
        context['admins_json'] = json.dumps(
            [{"id": a.id, "email": a.email, "exists": True}
                for a in self.conference.admins.all()] + 
            [{"id": a.id, "email": a.email, "exists": False}
                for a in self.conference.prospective_admins.all()]
        )
        return context

class ConferenceList(ListView):
    model = Conference
    def get_queryset(self):
        return Conference.objects.public_for(self.request.user)

class MasterSchedule(DetailView):
    model = Conference

    def get_object(self):
        return Conference.objects.get(random_slug=self.kwargs.get("slug"))

    def get_template_names(self):
        if "flat" in self.request.GET:
            return "schedule/master_schedule_flat.html"
        return "schedule/master_schedule.html"

    def render_to_response(self, context):
        if "ical" in self.request.GET:
            return self.render_ical(context)
        return super(MasterSchedule, self).render_to_response(context)

    def render_ical(self, context):
        ical = vobject.iCalendar()
        ical.add('method').value = 'PUBLISH'
        for chunk in context['chunks']:
            for event in chunk['events']:
                vevent = ical.add('vevent')
                vevent.add('summary').value = u" ".join([
                    event.title
                ])
                vevent.add('description').value = u"\n".join([
                    u"{}: {}".format(r.role, r.person) for r in event.eventrole_set.all()
                ])
                vevent.add('uid').value = unicode(event.guid)
                vevent.add('location').value = unicode(event.venue)
                vevent.add('dtstart').value = event.start_date
                vevent.add('dtend').value = event.end_date
                vevent.add('priority').value = '5'
                vevent.add('status').value = 'confirmed'
        icalstream = ical.serialize()
        response = HttpResponse(icalstream, content_type='text/calendar')
        response['Filename'] = 'events.ics'
        response['Content-Disposition'] = 'atachment: filename=events.ics'
        return response

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
                'period', 'venue', 'type', 'type__conference'
            ).prefetch_related(
                'eventrole_set', 'eventrole_set__person', 'eventrole_set__role',
            ).order_by('start_date', 'venue__name'))
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

        context["chunks"] = chunks
        context['ical_url'] = "{}{}?ical".format(settings.BASE_URL, self.request.path)
        context['is_admin'] = context['conference'].is_admin(self.request.user)
        return context

class PersonalSchedule(MasterSchedule):
    def get_object(self):
        self.conference = get_object_or_404(Conference, random_slug=self.kwargs['slug'])
        self.person = get_object_or_404(Person,
                conference=self.conference, pk=self.kwargs['pk'])
        return self.person.conference

    def event_filter(self, qs):
        return qs.filter(eventrole__person=self.person).distinct()

    def get_context_data(self, **kwargs):
        context = super(PersonalSchedule, self).get_context_data(**kwargs)
        context['filter'] = u"Schedule for {}".format(unicode(self.person))
        return context

class RoomSchedule(MasterSchedule):
    def get_object(self):
        self.venue = get_object_or_404(Venue, random_slug=self.kwargs['slug'])
        return self.venue.conference

    def event_filter(self, qs):
        return qs.filter(venue=self.venue).distinct()

    def get_context_data(self, **kwargs):
        context = super(RoomSchedule, self).get_context_data(**kwargs)
        context['filter'] = u"Schedule for {}".format(unicode(self.venue))
        return context

class PrintAll(DetailView):
    model = Conference
    template_name = "schedule/print_all.html"

    def get_object(self):
        return get_object_or_404(Conference, random_slug=self.kwargs.get("slug"))

    def get_context_data(self):
        context = super(PrintAll, self).get_context_data()
        events = {}
        for event in Event.objects.filter(conference=context['object']):
            events[event.pk] = event

        events = Event.objects.filter(
                conference=context['object']
            ).select_related(
                'venue', 'period'
            ).prefetch_related(
                'eventrole_set',
                'eventrole_set__person',
                'eventrole_set__role'
            ).order_by('start_date')
        people = defaultdict(lambda: {"events": []})
        for event in events:
            for eventrole in event.eventrole_set.all():
                if eventrole.person:
                    people[eventrole.person_id]['events'].append(event)
                    people[eventrole.person_id]['person'] = eventrole.person

        for person_id, person_context in people.iteritems():
            person_context['ical_url'] = "".join((
                settings.BASE_URL,
                reverse('personal_schedule', args=[
                    context['conference'].random_slug, person_context['person'].id
                ]),
                "?ical"
            ))

        context['people'] = people.values()
        context['people'].sort(key=lambda p: p['person'].name)
        return context

def edit_event(request, slug):
    conference = get_object_or_404(Conference.objects.active(), random_slug=slug)
    _admin_or_deny(request.user, conference)
    event_id = request.GET.get("id")
    if event_id:
        event = get_object_or_404(Event, pk=event_id)
    else:
        event = Event(conference=conference)
    if request.POST.get("delete"):
        event.delete()
        messages.info(request, "Event deleted.")
        return redirect("event_assigner", conference.random_slug)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        messages.info(request, "Event saved.")
        if request.POST.get("add_another"):
            return redirect("edit_event", conference.random_slug)
        return redirect("event_assigner", conference.random_slug)
    return render(request, "schedule/edit_event.html", {
        "conference": conference,
        "event": event,
        "form": form,
        "is_admin": conference.is_admin(request.user)
    })

class VenueCrud(GenericView):
    def _get_conference(self, slug):
        return get_object_or_404(Conference.objects.active(), random_slug=slug)

    def get(self, request, slug):
        conference = self._get_conference(slug)
        _admin_or_deny(request.user, conference)
        form = VenueForm(request.POST or None)
        form.is_valid()
        return render(request, "schedule/venue_crud.html", {
            "form": form,
            "is_admin": conference.is_admin(request.user),
            "conference": conference,
            "object_list": Venue.objects.filter(conference=conference).annotate(
                event_count=Count('event'))
        })

    def post(self, request, slug):
        conference = self._get_conference(slug)
        _admin_or_deny(request.user, conference)
        form = VenueForm(request.POST)
        if form.is_valid():
            Venue.objects.get_or_create(
                    conference=conference,
                    name=request.POST.get("name"))
            messages.success(request, "Venue added")
            return redirect("venue_crud", conference.random_slug) 
        return self.get()

    def delete(self, request, slug):
        params = QueryDict(request.body)
        venue = get_object_or_404(Venue, pk=params.get("venueId"))
        _admin_or_deny(request.user, venue.conference)
        venue.delete()
        messages.success(request, "Venue deleted")
        return HttpResponse()

class PersonCrud(GenericView):
    def get(self, request, slug):
        conference = get_object_or_404(Conference, random_slug=slug)
        form = PersonForm(request.POST or None)
        form.is_valid()
        return render(request, "schedule/person_crud.html", {
            "conference": conference,
            "form": form,
            "is_admin": conference.is_admin(self.request.user),
            "object_list": Person.objects.filter(
                conference=conference
            ).annotate(event_count=Count('eventrole')),
        })

    def post(self, request, slug):
        conference = get_object_or_404(Conference, random_slug=slug)
        _admin_or_deny(request.user, conference)
        form = PersonForm(request.POST or None)
        if form.is_valid():
            person, created = Person.objects.get_or_create(
                conference=conference,
                **form.cleaned_data
            )
            messages.success(request, "Person added")
            return redirect("person_crud", conference.random_slug)
        return self.get(request, slug)

    def delete(self, request, slug):
        conference = get_object_or_404(Conference, random_slug=slug)
        _admin_or_deny(request.user, conference)
        params = QueryDict(request.body)
        person = get_object_or_404(Person, conference=conference, pk=params.get("personId"))
        person.delete()
        messages.success(request, "Person removed")
        return HttpResponse()

class RoleTypeCrud(GenericView):
    def get(self, request, slug):
        conference = get_object_or_404(Conference.objects.active(), random_slug=slug)
        form = RoleTypeForm(request.POST or None)
        form.is_valid()
        object_list = RoleType.objects.filter(conference=conference).annotate(
                role_count=Count('eventrole'),
                person_count=Count('eventrole__person'))
        return render(request, "schedule/roletype_crud.html", {
                'conference': conference,
                'form': form,
                'is_admin': conference.is_admin(request.user),
                'object_list': object_list,
            })

    def post(self, request, slug):
        conference = get_object_or_404(Conference.objects.active(), random_slug=slug)
        _admin_or_deny(request.user, conference)
        form = RoleTypeForm(request.POST or None)
        if form.is_valid():
            RoleType.objects.get_or_create(
                    conference=conference,
                    role=self.request.POST.get("role"))
            messages.success(request, "Role type created")
            return redirect("roletype_crud", slug)
        return HttpResponse()

    def delete(self, request, slug):
        conference = get_object_or_404(Conference.objects.active(), random_slug=slug)
        _admin_or_deny(request.user, conference)
        params = QueryDict(request.body)
        roletype = get_object_or_404(RoleType, pk=params.get("roleTypeId"))
        roletype.delete()
        messages.success(request, "Role type deleted")
        return HttpResponse()

class AirportDesires(ListView):
    model = Person
    template_name = "schedule/airport_list.html"

    def get_queryset(self):
        self.conference = get_object_or_404(Conference, random_slug=self.kwargs['slug'])
        return Person.objects.filter(conference=self.conference).filter(
                Q(want_airport_pickup=True) | Q(want_airport_dropoff=True))

    def get_context_data(self, **kwargs):
        context = super(AirportDesires, self).get_context_data()
        context['conference'] = self.conference
        context["is_admin"] = self.conference.is_admin(self.request.user),
        return context

class EventAssigner(ListView):
    template_name = "schedule/event_assigner.html"

    def dispatch(self, request, *args, **kwargs):
        self.conference = get_object_or_404(Conference, random_slug=self.kwargs['slug'])
        problems = auth_problems(request.user, self.conference)
        if problems:
            return _problem_response(request, problems)
        return super(EventAssigner, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Event.objects.filter(
                conference=self.conference
            ).select_related(
                'venue', 'period',
            ).order_by('start_date').prefetch_related(
                'eventrole_set', 'eventrole_set__person', 'eventrole_set__role'
            )

    def get_context_data(self, **kwargs):
        context = super(EventAssigner, self).get_context_data(**kwargs)
        _add_event_context(context, self.conference)
        context['is_admin'] = self.conference.is_admin(self.request.user)
        return context

def _add_event_context(context, conference):
    context['conference'] = conference
    context['role_types'] = list(conference.roletype_set.all())
    context["venues"] = list(conference.venue_set.all())
    return context


class EventRoleAjaxCrud(GenericView):
    def post(self, request):
        event = get_object_or_404(Event.objects.select_related("conference"),
                pk=request.POST.get("eventId"))
        _admin_or_deny(request.user, event.conference)

        person_id = request.POST.get("person")
        if person_id:
            person = get_object_or_404(
                Person.objects.filter(conference=event.conference),
                pk=request.POST.get("person")
            )
        else:
            person = None

        roletype = get_object_or_404(
                RoleType.objects.filter(conference=event.conference),
                pk=request.POST.get("role"))

        eventrole_id = request.POST.get("eventRoleId")
        if eventrole_id:
            role = get_object_or_404(
                    EventRole.objects.filter(event=event),
                    pk=eventrole_id)
            role.person = person
            role.role = roletype
            role.save()
        else:
            role = EventRole.objects.create(
                event=event,
                person=person,
                role=roletype)
        event.eventrole_set.add(role)
        context = {"event": event}
        _add_event_context(context, event.conference)
        return render(request, "schedule/_event_role_row.html", context)

    def delete(self, request):
        params = QueryDict(request.body) 
        role = get_object_or_404(EventRole, pk=params.get("eventRoleId"))
        event = role.event
        _admin_or_deny(request.user, event.conference)

        role.delete()
        context = {"event": event}
        _add_event_context(context, event.conference)
        return render(request, "schedule/_event_role_row.html", context)

def update_event_attribute(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    event = get_object_or_404(
            Event.objects.select_related('conference'),
            pk=request.POST.get("eventId"))
    _admin_or_deny(request.user, event.conference)
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
    _admin_or_deny(request.user, event.conference)
    role_type = get_object_or_404(RoleType, pk=request.GET.get("roleTypeId"))
    event_role_id = request.GET.get("eventRoleId", None)

    people = list(Person.objects.filter(conference=event.conference))
    people_ids = [p.id for p in people]
    preferences = set(RolePreference.objects.filter(person__in=people_ids,
        roletype=role_type).values_list('person_id', flat=True))
    other_commitments = set(OtherCommitment.objects.filter(person__in=people,
        start_date__lt=event.end_date, end_date__gt=event.start_date
    ).values_list('person_id', flat=True))
    
    conflicting_roles = {}
    qs = EventRole.objects.filter(
        event__conference=event.conference,
        event__start_date__lt=event.end_date,
        event__end_date__gt=event.start_date,
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

def get_available_venues(request):
    event = get_object_or_404(Event, pk=request.GET.get("eventId"))
    venues = Venue.objects.filter(conference=event.conference)
    assignments = {}
    for venue_id,title in Event.objects.filter(
                conference=event.conference,
                venue__isnull=False,
                start_date__lt=event.end_date,
                end_date__gt=event.start_date
            ).exclude(pk=event.id).values_list('venue_id', 'title'):
        assignments[venue_id] = title

    results = [{
        "id": v.id,
        "text": v.name,
        "assigned": assignments[v.id] if v.id in assignments else None
    } for v in venues]
    results.sort(key=lambda r: (bool(r["assigned"]), r["text"]))

    res = json.dumps({"more": False, "results": results})
    return HttpResponse(res, content_type="application/json")

def get_admin_data(request):
    email = request.GET.get("email")
    if email:
        email = email.lower()
        try:
            user = User.objects.get(email=email)
            res = json.dumps({"id": user.id, "email": user.email, "exists": True}) 
        except User.DoesNotExist:
            try:
                user = ProspectiveAdmin.objects.get(email=email)
                res = json.dumps({"id": user.id, "email": user.email, "exists": False}) 
            except ProspectiveAdmin.DoesNotExist:
                # Fake it -- id as email
                res = json.dumps({"id": email, "email": email, "exists": False})
        return HttpResponse(res, content_type="application/json")
    return HttpResponseBadRequest("Missing 'email' query arg")

class AvailabilitySurvey(UpdateView):
    model = Person
    form_class = AvailabilityForm
    template_name = "schedule/availability.html"

    def get_object(self):
        return Person.objects.get(random_slug=self.kwargs['slug'])

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
