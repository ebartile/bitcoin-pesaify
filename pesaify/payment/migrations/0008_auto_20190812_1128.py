# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-08-12 08:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_auto_20190805_2310'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cryptoinfo',
            name='ex_rates',
        ),
        migrations.RemoveField(
            model_name='exrates',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='exrates',
            name='usd',
        ),
        migrations.RemoveField(
            model_name='minerfeesbtc',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='paymenturls',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='supportedtransactioncurrenciesbtc',
            name='invoice',
        ),
        migrations.AddField(
            model_name='exrates',
            name='currency',
            field=models.CharField(blank=True, choices=[('BTC', 'BTC - Bitcoin'), ('BCH', 'BCH - Bitcoin Cash'), ('USD', 'USD - US Dollar'), ('EUR', 'EUR - Eurozone Euro'), ('GBP', 'GBP - Pound Sterling'), ('JPY', 'JPY - Japanese Yen'), ('CAD', 'CAD - Canadian Dollar'), ('AUD', 'AUD - Australian Dollar'), ('CNY', 'CNY - Chinese Yuan'), ('CHF', 'CHF - Swiss Franc'), ('SEK', 'SEK - Swedish Krona'), ('NZD', 'NZD - New Zealand Dollar'), ('KRW', 'KRW - South Korean Won'), ('AED', 'AED - UAE Dirham '), ('AFN', 'AFN - Afghan Afghani '), ('ALL', 'ALL - Albanian Lek '), ('AMD', 'AMD - Armenian Dram '), ('ANG', 'ANG - Netherlands Antillean Guilder '), ('AOA', 'AOA - Angolan Kwanza '), ('ARS', 'ARS - Argentine Peso '), ('AWG', 'AWG - Aruban Florin '), ('AZN', 'AZN - Azerbaijani Manat '), ('BAM', 'BAM - Bosnia-Herzegovina Convertible Mark '), ('BBD', 'BBD - Barbadian Dollar '), ('BDT', 'BDT - Bangladeshi Taka '), ('BGN', 'BGN - Bulgarian Lev '), ('BHD', 'BHD - Bahraini Dinar '), ('BIF', 'BIF - Burundian Franc '), ('BMD', 'BMD - Bermudan Dollar '), ('BND', 'BND - Brunei Dollar '), ('BOB', 'BOB - Bolivian Boliviano '), ('BRL', 'BRL - Brazilian Real '), ('BSD', 'BSD - Bahamian Dollar '), ('BTN', 'BTN - Bhutanese Ngultrum '), ('BWP', 'BWP - Botswanan Pula '), ('BYN', 'BYN - Belarusian Ruble '), ('BZD', 'BZD - Belize Dollar '), ('CDF', 'CDF - Congolese Franc '), ('CLF', 'CLF - Chilean Unit of Account (UF) '), ('CLP', 'CLP - Chilean Peso '), ('COP', 'COP - Colombian Peso '), ('CRC', 'CRC - Costa Rican Colón '), ('CUP', 'CUP - Cuban Peso '), ('CVE', 'CVE - Cape Verdean Escudo '), ('CZK', 'CZK - Czech Koruna '), ('DJF', 'DJF - Djiboutian Franc '), ('DKK', 'DKK - Danish Krone '), ('DOP', 'DOP - Dominican Peso '), ('DZD', 'DZD - Algerian Dinar '), ('EGP', 'EGP - Egyptian Pound '), ('ETB', 'ETB - Ethiopian Birr '), ('FJD', 'FJD - Fijian Dollar '), ('FKP', 'FKP - Falkland Islands Pound '), ('GEL', 'GEL - Georgian Lari '), ('GHS', 'GHS - Ghanaian Cedi '), ('GIP', 'GIP - Gibraltar Pound '), ('GMD', 'GMD - Gambian Dalasi '), ('GNF', 'GNF - Guinean Franc '), ('GTQ', 'GTQ - Guatemalan Quetzal '), ('GUSD', 'GUSD - Gemini US Dollar '), ('GYD', 'GYD - Guyanaese Dollar '), ('HKD', 'HKD - Hong Kong Dollar '), ('HNL', 'HNL - Honduran Lempira '), ('HRK', 'HRK - Croatian Kuna '), ('HTG', 'HTG - Haitian Gourde '), ('HUF', 'HUF - Hungarian Forint '), ('IDR', 'IDR - Indonesian Rupiah '), ('ILS', 'ILS - Israeli Shekel '), ('INR', 'INR - Indian Rupee '), ('IQD', 'IQD - Iraqi Dinar '), ('IRR', 'IRR - Iranian Rial '), ('ISK', 'ISK - Icelandic Króna '), ('JEP', 'JEP - Jersey Pound '), ('JMD', 'JMD - Jamaican Dollar '), ('JOD', 'JOD - Jordanian Dinar '), ('KES', 'KES - Kenyan Shilling '), ('KGS', 'KGS - Kyrgystani Som '), ('KHR', 'KHR - Cambodian Riel '), ('KMF', 'KMF - Comorian Franc '), ('KPW', 'KPW - North Korean Won '), ('KWD', 'KWD - Kuwaiti Dinar '), ('KYD', 'KYD - Cayman Islands Dollar '), ('KZT', 'KZT - Kazakhstani Tenge '), ('LAK', 'LAK - Laotian Kip '), ('LBP', 'LBP - Lebanese Pound '), ('LKR', 'LKR - Sri Lankan Rupee '), ('LRD', 'LRD - Liberian Dollar '), ('LSL', 'LSL - Lesotho Loti '), ('LYD', 'LYD - Libyan Dinar '), ('MAD', 'MAD - Moroccan Dirham '), ('MDL', 'MDL - Moldovan Leu '), ('MGA', 'MGA - Malagasy Ariary '), ('MKD', 'MKD - Macedonian Denar '), ('MMK', 'MMK - Myanma Kyat '), ('MNT', 'MNT - Mongolian Tugrik '), ('MOP', 'MOP - Macanese Pataca '), ('MRU', 'MRU - Mauritanian Ouguiya '), ('MUR', 'MUR - Mauritian Rupee '), ('MVR', 'MVR - Maldivian Rufiyaa '), ('MWK', 'MWK - Malawian Kwacha'), ('MXN', 'MXN - Mexican Peso '), ('MYR', 'MYR - Malaysian Ringgit '), ('MZN', 'MZN - Mozambican Metical '), ('NAD', 'NAD - Namibian Dollar '), ('NGN', 'NGN - Nigerian Naira '), ('NIO', 'NIO - Nicaraguan Córdoba '), ('NOK', 'NOK - Norwegian Krone '), ('NPR', 'NPR - Nepalese Rupee '), ('OMR', 'OMR - Omani Rial '), ('PAB', 'PAB - Panamanian Balboa '), ('PEN', 'PEN - Peruvian Nuevo Sol '), ('PGK', 'PGK - Papua New Guinean Kina '), ('PHP', 'PHP - Philippine Peso '), ('PKR', 'PKR - Pakistani Rupee '), ('PLN', 'PLN - Polish Zloty '), ('PYG', 'PYG - Paraguayan Guarani '), ('QAR', 'QAR - Qatari Rial '), ('RON', 'RON - Romanian Leu '), ('RSD', 'RSD - Serbian Dinar '), ('RUB', 'RUB - Russian Ruble '), ('RWF', 'RWF - Rwandan Franc '), ('SAR', 'SAR - Saudi Riyal '), ('SBD', 'SBD - Solomon Islands Dollar '), ('SCR', 'SCR - Seychellois Rupee '), ('SDG', 'SDG - Sudanese Pound '), ('SGD', 'SGD - Singapore Dollar '), ('SHP', 'SHP - Saint Helena Pound '), ('SLL', 'SLL - Sierra Leonean Leone '), ('SOS', 'SOS - Somali Shilling '), ('SRD', 'SRD - Surinamese Dollar '), ('STN', 'STN - São Tomé and Príncipe Dobra '), ('SVC', 'SVC - Salvadoran Colón '), ('SYP', 'SYP - Syrian Pound '), ('SZL', 'SZL - Swazi Lilangeni '), ('THB', 'THB - Thai Baht '), ('TJS', 'TJS - Tajikistani Somoni '), ('TMT', 'TMT - Turkmenistani Manat '), ('TND', 'TND - Tunisian Dinar '), ('TOP', 'TOP - Tongan Paʻanga '), ('TRY', 'TRY - Turkish Lira '), ('TTD', 'TTD - Trinidad and Tobago Dollar '), ('TWD', 'TWD - New Taiwan Dollar '), ('TZS', 'TZS - Tanzanian Shilling '), ('UAH', 'UAH - Ukrainian Hryvnia '), ('UGX', 'UGX - Ugandan Shilling '), ('USDC', 'USDC - Circle USD Coin '), ('UYU', 'UYU - Uruguayan Peso '), ('UZS', 'UZS - Uzbekistan Som '), ('VEF', 'VEF - Venezuelan Bolívar Fuerte '), ('VES', 'VES - Venezuelan Bolívar Soberano '), ('VND', 'VND - Vietnamese Dong '), ('VUV', 'VUV - Vanuatu Vatu '), ('WST', 'WST - Samoan Tala '), ('XAF', 'XAF - CFA Franc BEAC '), ('XCD', 'XCD - East Caribbean Dollar '), ('XOF', 'XOF - CFA Franc BCEAO '), ('XPF', 'XPF - CFP Franc '), ('YER', 'YER - Yemeni Rial '), ('ZAR', 'ZAR - South African Rand '), ('ZMW', 'ZMW - Zambian Kwacha '), ('ZWL', 'ZWL - Zimbabwean Dollar '), ('XAG', 'XAG - Silver (troy ounce) '), ('XAU', 'XAU - Gold (troy ounce) ')], default='BTC', max_length=256, verbose_name='currency'),
        ),
        migrations.AddField(
            model_name='exrates',
            name='rate',
            field=models.IntegerField(default=0, verbose_name='rate'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='address',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='address'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='crypto_code',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='crypto code'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='crypto_paid',
            field=models.FloatField(default=0, verbose_name='crypto paid'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='due',
            field=models.FloatField(default=0, verbose_name='due'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='network_fee',
            field=models.FloatField(default=0, verbose_name='network fee'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='paid',
            field=models.FloatField(default=0, verbose_name='paid'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='payment_type',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='payment type'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='price',
            field=models.FloatField(default=0, verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='total_due',
            field=models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='total due'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='tx_count',
            field=models.IntegerField(default=0, verbose_name='tx count'),
        ),
        migrations.AlterField(
            model_name='cryptoinfo',
            name='url',
            field=models.URLField(blank=True, default='', max_length=1000, null=True, verbose_name='url'),
        ),
    ]
