# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0002_auto_20141029_0525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='note',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
