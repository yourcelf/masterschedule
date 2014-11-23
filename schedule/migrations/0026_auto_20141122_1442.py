# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0025_auto_20141116_1503'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProspectiveAdmin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='conference',
            name='prospective_admins',
            field=models.ManyToManyField(to='schedule.ProspectiveAdmin', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='conference',
            name='public',
            field=models.BooleanField(default=True, help_text=b'List this conference on the front page?'),
        ),
        migrations.AlterUniqueTogether(
            name='venue',
            unique_together=set([('conference', 'name')]),
        ),
    ]
