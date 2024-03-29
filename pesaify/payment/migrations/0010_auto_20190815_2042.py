# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-08-15 17:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0009_auto_20190812_1215'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice',
            options={'ordering': ['current_time']},
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='created_date',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='modified_date',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='url',
        ),
        migrations.AddField(
            model_name='invoice',
            name='itype',
            field=models.CharField(choices=[('checkout', 'Checkout'), ('email', 'Email'), ('pos', 'Point of Sale'), ('button', 'Button'), ('catalog', 'Catalog')], default='checkout', max_length=30, verbose_name='type'),
        ),
    ]
