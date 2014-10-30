# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0005_auto_20141029_0534'),
    ]

    operations = [
        migrations.AddField(
			model_name="publication", 
			name="issn", 
			field=models.CharField(max_length=32,verbose_name="ISSN",blank=True),
            preserve_default=True
		),
    ]
