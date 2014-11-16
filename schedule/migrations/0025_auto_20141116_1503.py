# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0024_auto_20141116_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='archived',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='airport_dropoff_date',
            field=models.DateTimeField(help_text=b'When do you need to be at the airport? (e.g. one hour before flight departure)', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='airport_pickup_date',
            field=models.DateTimeField(help_text=b'When do you arrive at the airport?', null=True, blank=True),
            preserve_default=True,
        ),
    ]
