# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_auto_20141016_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='availability_end_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='availability_start_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
