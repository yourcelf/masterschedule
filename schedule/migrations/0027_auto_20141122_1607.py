# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0026_auto_20141122_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='prospective_admins',
            field=models.ManyToManyField(to=b'schedule.ProspectiveAdmin', null=True, blank=True),
        ),
    ]
