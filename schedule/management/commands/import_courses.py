import re
import csv
import datetime
import pytz

from django.core.management.base import BaseCommand
from django.conf import settings
from schedule.models import *

tz = pytz.timezone(settings.TIME_ZONE)
conference = Conference.objects.get(pk=1)

class Command(BaseCommand):
    def add_argument(self, parser):
        parser.add_argument("csv_file", type=unicode) 

    def handle(self, *args, **kwargs):
        csv_file = args[0]
        with open(csv_file) as fh:
            reader = csv.reader(fh)
            first = True
            for block, times, presenters, title, url in reader:
                if first:
                    first = False
                    continue
                period = Period.objects.get(conference=conference, period=block)
                event_type = EventType.objects.get(conference=conference, type="Course")
                names = presenters.split(" and ")
                names = [re.sub("\([^\)]+\)", "", n).strip() for n in names]
                people = [Person.objects.get_or_create(name=n, conference=conference)[0] for n in names]
                event, created = Event.objects.get_or_create(
                    conference=conference,
                    title=title,
                    period=period,
                    type=event_type,
                )
                for person in people:
                    EventRole.objects.get_or_create(
                            event=event,
                            role="Presenter",
                            person=person)

