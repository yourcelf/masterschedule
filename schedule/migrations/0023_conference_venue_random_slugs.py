# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

from schedule.models import random_slug

def set_random_slugs(apps, schema_editor):
    for model in ("Conference", "Venue"):
        Model = apps.get_model("schedule", model)
        for obj in Model.objects.all():
            if not obj.random_slug:
                obj.random_slug = random_slug()
                obj.save()

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedule', '0022_auto_20141107_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='admins',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conference',
            name='public',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conference',
            name='random_slug',
            field=models.CharField(default='', max_length=64, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venue',
            name='random_slug',
            field=models.CharField(default='', max_length=64, editable=False),
            preserve_default=False,
        ),
        migrations.RunPython(set_random_slugs),
    ]
