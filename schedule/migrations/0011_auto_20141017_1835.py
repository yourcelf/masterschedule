# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def populate_role_fks(apps, schema_editor):
    EventRole = apps.get_model('schedule', 'EventRole')
    RoleType = apps.get_model('schedule', 'RoleType')
    for role in EventRole.objects.all():
        role.role = RoleType.objects.get_or_create(
                conference=role.event.conference,
                role=role.role_text)[0]
        role.save()


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0010_eventrole_role'),
    ]

    operations = [
        migrations.RunPython(populate_role_fks, lambda a,b: None)
    ]
