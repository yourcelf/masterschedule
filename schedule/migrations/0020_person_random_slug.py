# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import base64

from django.db import models, migrations

def set_random_slugs(apps, schema_editor):
    """
    Saving populates the random slug.
    """
    Person = apps.get_model("schedule", "Person")
    for person in Person.objects.all():
        # Duplicate implementation of `set_random_slug` from person models.
        person.random_slug = base64.urlsafe_b64encode(
            os.urandom(32)
        ).replace("=", "%3D")
        person.save()

class Migration(migrations.Migration):
    dependencies = [
        ('schedule', '0019_auto_20141102_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='random_slug',
            field=models.CharField(default='', max_length=64, editable=False),
            preserve_default=False,
        ),
        migrations.RunPython(set_random_slugs),
    ]
