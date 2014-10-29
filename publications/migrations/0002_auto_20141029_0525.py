# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='year',
            field=models.PositiveIntegerField(max_length=4, null=True, blank=True),
            preserve_default=True,
        ),
    ]
