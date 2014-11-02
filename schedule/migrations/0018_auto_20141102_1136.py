# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0017_auto_20141018_1726'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventrole',
            options={'ordering': ['role']},
        ),
    ]
