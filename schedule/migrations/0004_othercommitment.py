# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0003_auto_20141016_2326'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherCommitment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('person', models.ForeignKey(to='schedule.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
