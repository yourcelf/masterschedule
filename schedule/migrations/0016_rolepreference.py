# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0015_auto_20141018_1331'),
    ]

    operations = [
        migrations.CreateModel(
            name='RolePreference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('person', models.ForeignKey(to='schedule.Person')),
                ('roletype', models.ForeignKey(to='schedule.RoleType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
