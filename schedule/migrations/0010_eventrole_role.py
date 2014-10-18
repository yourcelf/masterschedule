# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0009_remove_eventrole_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventrole',
            name='role',
            field=models.ForeignKey(blank=True, to='schedule.RoleType', null=True),
            preserve_default=True,
        ),
    ]
