import re
import csv
import datetime
import pytz

from django.core.management.base import BaseCommand
from django.conf import settings
from schedule.models import *

tz = pytz.timezone(settings.TIME_ZONE)
conference = Conference.objects.get(pk=5) #XXX

BLOCKS = {
    "Friday Staff & Managers Pre-Conference": (
        datetime.datetime(2015, 10, 30, 9, 30, 0, 0, tz),
        datetime.datetime(2015, 10, 30, 17, 0, 0, 0, tz)
    ),
    "Course Block 1": (
        datetime.datetime(2015, 10, 31, 9, 0, 0, 0, tz),
        datetime.datetime(2015, 10, 31, 10, 30, 0, 0, tz),
    ),
    "Course Block 2": (
        datetime.datetime(2015, 10, 31, 10, 40, 0, 0, tz),
        datetime.datetime(2015, 10, 31, 12, 30, 0, 0, tz),
    ),
    "Course Block 3": (
        datetime.datetime(2015, 10, 31, 14, 45, 0, 0, tz),
        datetime.datetime(2015, 10, 31, 16, 15, 0, 0, tz),
    ),
    "Course Block 4": (
        datetime.datetime(2015, 10, 31, 16, 25, 0, 0, tz),
        datetime.datetime(2015, 10, 31, 17, 55, 0, 0, tz),
    ),
    "Course Block 5": (
        datetime.datetime(2015, 11, 01, 9, 0, 0, 0, tz),
        datetime.datetime(2015, 11, 01, 10, 30, 0, 0, tz),
    ),
    "Course Block 6": (
        datetime.datetime(2015, 11, 01, 10, 45, 0, 0, tz),
        datetime.datetime(2015, 11, 01, 12, 15, 0, 0, tz),
    ),
    "Course Block 7": (
        datetime.datetime(2015, 11, 01, 13, 45, 0, 0, tz),
        datetime.datetime(2015, 11, 01, 15, 15, 0, 0, tz),
    )
}

class Command(BaseCommand):
    def add_argument(self, parser):
        parser.add_argument("csv_file", type=unicode) 

    def handle(self, *args, **kwargs):
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

        role_type, created = RoleType.objects.get_or_create(
                conference=conference, role="Presenter"
        )

        for course in courses:
            period = Period.objects.get_or_create(
                conference=conference,
                period=course['block'],
                start_date=BLOCKS[course['block']][0],
                end_date=BLOCKS[course['block']][1],
            )[0]
            names = course['presenters'].split("; ")
            people = [Person.objects.get_or_create(name=n, conference=conference)[0] for n in names]
            event, created = Event.objects.get_or_create(
                conference=conference,
                title=course['title'],
                period=period,
            )
            for person in people:
                EventRole.objects.get_or_create(
                        event=event,
                        role=role_type,
                        person=person)
