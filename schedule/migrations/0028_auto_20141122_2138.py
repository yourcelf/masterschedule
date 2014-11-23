# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0027_auto_20141122_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='public',
            field=models.BooleanField(default=True, help_text=b'List this conference on the front page? Uncheck for more privacy.'),
        ),
        migrations.AlterField(
            model_name='prospectiveadmin',
            name='email',
            field=models.EmailField(unique=True, max_length=255),
        ),
    ]
