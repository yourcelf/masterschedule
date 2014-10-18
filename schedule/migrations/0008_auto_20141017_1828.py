# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def copy_role_names(apps, schema_editor):
    EventRole = apps.get_model('schedule', 'EventRole')
    for role in EventRole.objects.all():
        role.role_text = role.role
        role.save()

class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0007_auto_20141017_1826'),
    ]

    operations = [
        migrations.RunPython(copy_role_names, lambda a,b: None)
    ]
