# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0003_auto_20141029_0530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='keywords',
            field=models.TextField(help_text=b'List of keywords separated by commas.', blank=True),
            preserve_default=True,
        ),
    ]
