# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-05 16:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.CharField(max_length=200, unique=True)),
                ('check_in_time', models.DateTimeField(auto_now_add=True)),
                ('wait_time', models.DurationField(null=True)),
                ('status', models.CharField(default='', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AverageWaitTime',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('average_wait_time', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('', ''), ('UNK', 'Unknown'), ('ASKU', 'Declined to specify'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Other', max_length=1)),
                ('patient_id', models.IntegerField(unique=True)),
                ('doctor_id', models.IntegerField()),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('patient_photo', models.CharField(max_length=1000)),
            ],
        ),
        migrations.AddField(
            model_name='averagewaittime',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drchrono.Doctor'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drchrono.Patient'),
        ),
    ]
