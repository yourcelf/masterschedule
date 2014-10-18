# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0014_auto_20141018_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='attending',
            field=models.BooleanField(default=True, help_text=b'Are you attending?'),
        ),
    ]
