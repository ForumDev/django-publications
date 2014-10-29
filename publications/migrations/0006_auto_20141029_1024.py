# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0005_auto_20141029_0534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='citekey',
            field=models.CharField(help_text=b'BibTex citation key. Leave blank if unsure.', max_length=512, unique=True, null=True, blank=True),
            preserve_default=True,
        ),
    ]
