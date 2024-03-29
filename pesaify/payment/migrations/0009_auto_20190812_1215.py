# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-08-12 09:15
from __future__ import unicode_literals

import django.core.serializers.json
from django.db import migrations
import pesaify.base.db.models.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0008_auto_20190812_1128'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addresses',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='cryptoinfo',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='exchangerates',
            name='btc',
        ),
        migrations.RemoveField(
            model_name='exchangerates',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='flags',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='minerfees',
            name='btc',
        ),
        migrations.RemoveField(
            model_name='minerfees',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='paymentcodes',
            name='btc',
        ),
        migrations.RemoveField(
            model_name='paymentcodes',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='paymenttotals',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='supportedtransactioncurrencies',
            name='btc',
        ),
        migrations.RemoveField(
            model_name='supportedtransactioncurrencies',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='amount_paid',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='btc_due',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='btc_paid',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='btc_price',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='buyer_paid_btc_miner_fee',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='buyer_total_btc_amount',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='exception_status',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='guid',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='item_code',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='item_desc',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='low_fee_detected',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='order_id',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='price',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='rate',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='refund_address_request_pending',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='token',
        ),
        migrations.AddField(
            model_name='invoice',
            name='extra',
            field=pesaify.base.db.models.fields.json.JSONField(default={}, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.DeleteModel(
            name='Addresses',
        ),
        migrations.DeleteModel(
            name='CryptoInfo',
        ),
        migrations.DeleteModel(
            name='ExchangeRates',
        ),
        migrations.DeleteModel(
            name='ExRates',
        ),
        migrations.DeleteModel(
            name='Flags',
        ),
        migrations.DeleteModel(
            name='MinerFees',
        ),
        migrations.DeleteModel(
            name='MinerFeesBTC',
        ),
        migrations.DeleteModel(
            name='PaymentCodes',
        ),
        migrations.DeleteModel(
            name='Payments',
        ),
        migrations.DeleteModel(
            name='PaymentTotals',
        ),
        migrations.DeleteModel(
            name='PaymentUrls',
        ),
        migrations.DeleteModel(
            name='SupportedTransactionCurrencies',
        ),
        migrations.DeleteModel(
            name='SupportedTransactionCurrenciesBTC',
        ),
    ]
