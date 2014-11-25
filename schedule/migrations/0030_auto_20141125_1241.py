# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0029_auto_20141123_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='archived',
            field=models.BooleanField(default=False, help_text=b'Remove this conference from your list?'),
        ),
    ]
