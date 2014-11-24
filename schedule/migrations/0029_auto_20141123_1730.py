# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0028_auto_20141122_2138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventtype',
            name='conference',
        ),
        migrations.RemoveField(
            model_name='event',
            name='type',
        ),
        migrations.DeleteModel(
            name='EventType',
        ),
        migrations.RemoveField(
            model_name='event',
            name='url',
        ),
    ]
