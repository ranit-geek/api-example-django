# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-08 09:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='session_start_time',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]