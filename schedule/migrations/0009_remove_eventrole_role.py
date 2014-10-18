# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_auto_20141017_1828'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventrole',
            name='role',
        ),
    ]
