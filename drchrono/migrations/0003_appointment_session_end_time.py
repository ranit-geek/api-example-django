# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-08 10:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0002_auto_20190908_0958'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='session_end_time',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]