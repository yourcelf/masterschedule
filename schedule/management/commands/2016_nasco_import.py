import re
import unicodecsv as csv
import datetime
import pytz

from django.core.management.base import BaseCommand
from django.conf import settings
from schedule.models import *

tz = pytz.timezone(settings.TIME_ZONE)
conference_slug = "KQzNyPo4fQC1xHJnAX7weh9XAZijdgIRdppKc4O2Xsk="

def parse_date(datestr, timestr):
    naive = datetime.datetime.strptime(
            datestr + " " + timestr, "%m/%d/%y %I:%M:%S %p"
    )
    return tz.localize(naive)

class Command(BaseCommand):
    def add_argument(self, parser):
        parser.add_argument("csv_file", type=unicode) 

    def handle(self, *args, **kwargs):
        try:
            conference = Conference.objects.get(
                    random_slug=conference_slug
            )
        except Conference.DoesNotExist:
            conference = Conference.objects.create(
                name="NASCO Institute {}".format(datetime.datetime.now().strftime("%Y")),
                public=False,
                archived=False,
                random_slug=conference_slug,
            )

        courses_file = args[0]
        courses = []
        with open(courses_file) as fh:
            reader = csv.reader(fh)
            columns = []
            for i,row in enumerate(reader):
                if i == 0:
                    columns = row
                else:
                    courses.append(dict(zip(columns, row)))

        BLOCKS = {}
        for course in courses:
            BLOCKS[course['Period']] = (
                parse_date(course['Date'], course['Start Time']),
                parse_date(course['Date'], course['End Time'])
            )

        role_type, created = RoleType.objects.get_or_create(
                conference=conference, role="Presenter"
        )

        for course in courses:
            period, created = Period.objects.get_or_create(
                conference=conference,
                period=course['Period'],
            )
            period.start_date = BLOCKS[course['Period']][0]
            period.end_date = BLOCKS[course['Period']][1]
            period.save()

            venue, created = Venue.objects.get_or_create(
                conference=conference,
                name=course['Room']
            )

            event, created = Event.objects.get_or_create(
                conference=conference,
                title=course['Session Title'],
            )
            event.period = period
            event.venue = venue
            event.save()

            names = course.get('Presenter', '').split(";")
            people = [Person.objects.get_or_create(name=n.strip(), conference=conference)[0] for n in names]
            for person in people:
                EventRole.objects.get_or_create(
                        event=event,
                        role=role_type,
                        person=person)
