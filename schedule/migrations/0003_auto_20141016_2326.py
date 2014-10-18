# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20141016_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='airport_dropoff_details',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='airport_pickup_details',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
    ]
