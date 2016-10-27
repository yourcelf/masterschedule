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
    return datetime.datetime(naive.year, naive.month, naive.day,
            naive.hour, naive.minute, naive.second, 0, tz)

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
            period = Period.objects.get_or_create(
                conference=conference,
                period=course['Period'],
                start_date=BLOCKS[course['Period']][0],
                end_date=BLOCKS[course['Period']][1],
            )[0]

            event, created = Event.objects.get_or_create(
                conference=conference,
                title=course['Session Title'],
                period=period,
            )
            names = course.get('Presenters', '').split("; ")
            people = [Person.objects.get_or_create(name=n, conference=conference)[0] for n in names]
            for person in people:
                EventRole.objects.get_or_create(
                        event=event,
                        role=role_type,
                        person=person)
