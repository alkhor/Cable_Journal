# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-28 05:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connections', '0003_discover_data_switch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discover_data',
            name='port',
            field=models.TextField(default='-'),
        ),
        migrations.AlterField(
            model_name='discover_data',
            name='switch',
            field=models.TextField(default='-'),
        ),
    ]