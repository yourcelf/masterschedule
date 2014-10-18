# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0016_rolepreference'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='roletype',
            options={'ordering': ['role']},
        ),
    ]
