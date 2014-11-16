# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0023_conference_venue_random_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='random_slug',
            field=models.CharField(unique=True, max_length=64, editable=False),
        ),
        migrations.AlterField(
            model_name='person',
            name='random_slug',
            field=models.CharField(unique=True, max_length=64, editable=False),
        ),
        migrations.AlterField(
            model_name='venue',
            name='random_slug',
            field=models.CharField(unique=True, max_length=64, editable=False),
        ),
    ]
