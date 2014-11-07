# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.db import models, migrations

def add_guids(apps, schema_editor):
    Event = apps.get_model("schedule", "Event")
    for event in Event.objects.all():
        event.guid = str(uuid.uuid4())
        event.save()

class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0020_person_random_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='guid',
            field=models.CharField(default='', max_length=36),
            preserve_default=False,
        ),
        migrations.RunPython(add_guids),
    ]
