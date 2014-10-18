# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0006_auto_20141016_2328'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=70)),
                ('conference', models.ForeignKey(to='schedule.Conference')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='eventrole',
            name='role_text',
            field=models.CharField(default='', max_length=70),
            preserve_default=False,
        ),
    ]
