# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_othercommitment'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='want_airport_dropoff',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='want_airport_pickup',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
