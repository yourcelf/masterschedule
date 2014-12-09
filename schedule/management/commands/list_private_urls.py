from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse

from schedule.models import Conference

class Command(BaseCommand):
    def handle(self, conference_id, *args, **kwargs):
        conference = Conference.objects.get(pk=conference_id)
        urls = []
        urls.append(reverse("master_schedule", args=[conference.random_slug]))
        urls.append(reverse("airport_list", args=[conference.random_slug]))
        for venue in conference.venue_set.all():
            urls.append(reverse("venue_crud", args=[venue.random_slug]))
            urls.append(reverse("venue_schedule", args=[venue.random_slug]))
        for person in conference.person_set.all():
            urls.append(reverse("personal_schedule", args=[conference.random_slug, person.pk]))
            urls.append(reverse("availability_survey", args=[person.random_slug]))
        for url in urls:
            print url
