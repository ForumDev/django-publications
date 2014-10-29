# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0004_auto_20141029_0532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='url',
            field=models.URLField(help_text=b'Link to PDF or journal page.', max_length=1000, verbose_name=b'URL', blank=True),
            preserve_default=True,
        ),
    ]
