# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def unescape_equals(apps, schema_editor):
    Conference = apps.get_model("schedule", "Conference")
    Person = apps.get_model("schedule", "Person")
    Venue = apps.get_model("schedule", "Venue")
    for m in ["Conference", "Person", "Venue"]:
        Model = apps.get_model("schedule", m)
        for obj in Model.objects.all():
            obj.random_slug = obj.random_slug.replace("%3D", "=")
            obj.save()

class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0030_auto_20141125_1241'),
    ]

    operations = [
        migrations.RunPython(unescape_equals)
    ]
