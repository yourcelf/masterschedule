# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0013_auto_20141018_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='attending',
            field=models.BooleanField(default=False, help_text=b'Are you attending?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='airport_dropoff_details',
            field=models.TextField(help_text=b'Please list your flight information.', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='airport_pickup_details',
            field=models.TextField(help_text=b'Please list your flight information.', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='availability_end_date',
            field=models.DateTimeField(help_text=b'When do you leave?', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='availability_start_date',
            field=models.DateTimeField(help_text=b'When are you first available to volunteer?', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='want_airport_dropoff',
            field=models.BooleanField(default=False, help_text=b'Airport dropoffs might not be available.  But if we have capacity, would you like to get a ride?'),
        ),
        migrations.AlterField(
            model_name='person',
            name='want_airport_pickup',
            field=models.BooleanField(default=False, help_text=b'Airport pickups might not be available.  But if we have capacity, would you like to get a ride?'),
        ),
    ]
