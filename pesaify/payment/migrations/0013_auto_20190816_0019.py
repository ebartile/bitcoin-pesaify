# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-08-15 21:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0012_auto_20190815_2048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='bitcoin_address',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='status',
        ),
    ]
