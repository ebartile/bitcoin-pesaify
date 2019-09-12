# -*- coding: utf-8 -*-
#spring birth language math width service trial alley keen sustain improve initial
import uuid
import re
from django_countries import Countries
from django_countries.fields import CountryField
from django.core.validators import RegexValidator
from django.apps import apps
from datetime import datetime
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
from django.db.models.signals import post_save
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.contrib.postgres.fields import HStoreField
from django.db import migrations
from django.contrib.postgres.operations import HStoreExtension
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from pesaify.client import PesaifyClient

class Migration(migrations.Migration):

    operations = [
    ]

MOBILEMONEY = 'MM'
UG_SHS = 'UGX'
KEN_SHS = 'KES'
TZ_SHS = 'TZS'
EURO = 'EUR'
POUND = 'GBP'
US_DOLLAR = 'USD'
BITCOIN = 'BTC'
BITCASH = 'BCH'

MM_CURRENCY = (
    (MOBILEMONEY, 'Mobile Money (MM)'),
)

CRYPTO_CURRENCY = (
    (BITCOIN, 'Bitcoin (BTC)'),
    (BITCASH, 'Bitcash (BCH)'),
)

BANK_CURRENCY = (
    (UG_SHS, 'Uganda Shillings (UGX)'),
    (KEN_SHS, 'Kenya Shillings (KZS)'),
    (TZ_SHS, 'Tanzania Shillings (TZS)'),
    (EURO, 'European Euro (EUR)'),
    (POUND, 'Pound Sterling (GBP)'),
    (US_DOLLAR, 'US Dollar (USD)'),
)

CURRENT = 'Current'
FIXED = 'Fixed'

REFUND = (
    (CURRENT, 'Current'),
    (FIXED, 'Fixed')
)

CURRENCY = (
    ("BTC", "BTC - Bitcoin"),
    ("BCH", "BCH - Bitcoin Cash"),
    ("USD", "USD - US Dollar"),
    ("EUR", "EUR - Eurozone Euro"),
    ("GBP", "GBP - Pound Sterling"),
    ("JPY", "JPY - Japanese Yen"),
    ("CAD", "CAD - Canadian Dollar"),
    ("AUD", "AUD - Australian Dollar"),
    ("CNY", "CNY - Chinese Yuan"),
    ("CHF", "CHF - Swiss Franc"),
    ("SEK", "SEK - Swedish Krona"),
    ("NZD", "NZD - New Zealand Dollar"),
    ("KRW", "KRW - South Korean Won"),
    ("AED", "AED - UAE Dirham "),
    ("AFN", "AFN - Afghan Afghani "),
    ("ALL", "ALL - Albanian Lek "),
    ("AMD", "AMD - Armenian Dram "),
    ("ANG", "ANG - Netherlands Antillean Guilder "),
    ("AOA", "AOA - Angolan Kwanza "),
    ("ARS", "ARS - Argentine Peso "),
    ("AWG", "AWG - Aruban Florin "),
    ("AZN", "AZN - Azerbaijani Manat "),
    ("BAM", "BAM - Bosnia-Herzegovina Convertible Mark "),
    ("BBD", "BBD - Barbadian Dollar "),
    ("BDT", "BDT - Bangladeshi Taka "),
    ("BGN", "BGN - Bulgarian Lev "),
    ("BHD", "BHD - Bahraini Dinar "),
    ("BIF", "BIF - Burundian Franc "),
    ("BMD", "BMD - Bermudan Dollar "),
    ("BND", "BND - Brunei Dollar "),
    ("BOB", "BOB - Bolivian Boliviano "),
    ("BRL", "BRL - Brazilian Real "),
    ("BSD", "BSD - Bahamian Dollar "),
    ("BTN", "BTN - Bhutanese Ngultrum "),
    ("BWP", "BWP - Botswanan Pula "),
    ("BYN", "BYN - Belarusian Ruble "),
    ("BZD", "BZD - Belize Dollar "),
    ("CDF", "CDF - Congolese Franc "),
    ("CLF", "CLF - Chilean Unit of Account (UF) "),
    ("CLP", "CLP - Chilean Peso "),
    ("COP", "COP - Colombian Peso "),
    ("CRC", "CRC - Costa Rican Colón "),
    ("CUP", "CUP - Cuban Peso "),
    ("CVE", "CVE - Cape Verdean Escudo "),
    ("CZK", "CZK - Czech Koruna "),
    ("DJF", "DJF - Djiboutian Franc "),
    ("DKK", "DKK - Danish Krone "),
    ("DOP", "DOP - Dominican Peso "),
    ("DZD", "DZD - Algerian Dinar "),
    ("EGP", "EGP - Egyptian Pound "),
    ("ETB", "ETB - Ethiopian Birr "),
    ("FJD", "FJD - Fijian Dollar "),
    ("FKP", "FKP - Falkland Islands Pound "),
    ("GEL", "GEL - Georgian Lari "),
    ("GHS", "GHS - Ghanaian Cedi "),
    ("GIP", "GIP - Gibraltar Pound "),
    ("GMD", "GMD - Gambian Dalasi "),
    ("GNF", "GNF - Guinean Franc "),
    ("GTQ", "GTQ - Guatemalan Quetzal "),
    ("GUSD", "GUSD - Gemini US Dollar "),
    ("GYD", "GYD - Guyanaese Dollar "),
    ("HKD", "HKD - Hong Kong Dollar "),
    ("HNL", "HNL - Honduran Lempira "),
    ("HRK", "HRK - Croatian Kuna "),
    ("HTG", "HTG - Haitian Gourde "),
    ("HUF", "HUF - Hungarian Forint "),
    ("IDR", "IDR - Indonesian Rupiah "),
    ("ILS", "ILS - Israeli Shekel "),
    ("INR", "INR - Indian Rupee "),
    ("IQD", "IQD - Iraqi Dinar "),
    ("IRR", "IRR - Iranian Rial "),
    ("ISK", "ISK - Icelandic Króna "),
    ("JEP", "JEP - Jersey Pound "),
    ("JMD", "JMD - Jamaican Dollar "),
    ("JOD", "JOD - Jordanian Dinar "),
    ("KES", "KES - Kenyan Shilling "),
    ("KGS", "KGS - Kyrgystani Som "),
    ("KHR", "KHR - Cambodian Riel "),
    ("KMF", "KMF - Comorian Franc "),
    ("KPW", "KPW - North Korean Won "),
    ("KWD", "KWD - Kuwaiti Dinar "),
    ("KYD", "KYD - Cayman Islands Dollar "),
    ("KZT", "KZT - Kazakhstani Tenge "),
    ("LAK", "LAK - Laotian Kip "),
    ("LBP", "LBP - Lebanese Pound "),
    ("LKR", "LKR - Sri Lankan Rupee "),
    ("LRD", "LRD - Liberian Dollar "),
    ("LSL", "LSL - Lesotho Loti "),
    ("LYD", "LYD - Libyan Dinar "),
    ("MAD", "MAD - Moroccan Dirham "),
    ("MDL", "MDL - Moldovan Leu "),
    ("MGA", "MGA - Malagasy Ariary "),
    ("MKD", "MKD - Macedonian Denar "),
    ("MMK", "MMK - Myanma Kyat "),
    ("MNT", "MNT - Mongolian Tugrik "),
    ("MOP", "MOP - Macanese Pataca "),
    ("MRU", "MRU - Mauritanian Ouguiya "),
    ("MUR", "MUR - Mauritian Rupee "),
    ("MVR", "MVR - Maldivian Rufiyaa "),
    ("MWK", "MWK - Malawian Kwacha"),
    ("MXN", "MXN - Mexican Peso "),
    ("MYR", "MYR - Malaysian Ringgit "),
    ("MZN", "MZN - Mozambican Metical "),
    ("NAD", "NAD - Namibian Dollar "),
    ("NGN", "NGN - Nigerian Naira "),
    ("NIO", "NIO - Nicaraguan Córdoba "),
    ("NOK", "NOK - Norwegian Krone "),
    ("NPR", "NPR - Nepalese Rupee "),
    ("OMR", "OMR - Omani Rial "),
    ("PAB", "PAB - Panamanian Balboa "),
    ("PEN", "PEN - Peruvian Nuevo Sol "),
    ("PGK", "PGK - Papua New Guinean Kina "),
    ("PHP", "PHP - Philippine Peso "),
    ("PKR", "PKR - Pakistani Rupee "),
    ("PLN", "PLN - Polish Zloty "),
    ("PYG", "PYG - Paraguayan Guarani "),
    ("QAR", "QAR - Qatari Rial "),
    ("RON", "RON - Romanian Leu "),
    ("RSD", "RSD - Serbian Dinar "),
    ("RUB", "RUB - Russian Ruble "),
    ("RWF", "RWF - Rwandan Franc "),
    ("SAR", "SAR - Saudi Riyal "),
    ("SBD", "SBD - Solomon Islands Dollar "),
    ("SCR", "SCR - Seychellois Rupee "),
    ("SDG", "SDG - Sudanese Pound "),
    ("SGD", "SGD - Singapore Dollar "),
    ("SHP", "SHP - Saint Helena Pound "),
    ("SLL", "SLL - Sierra Leonean Leone "),
    ("SOS", "SOS - Somali Shilling "),
    ("SRD", "SRD - Surinamese Dollar "),
    ("STN", "STN - São Tomé and Príncipe Dobra "),
    ("SVC", "SVC - Salvadoran Colón "),
    ("SYP", "SYP - Syrian Pound "),
    ("SZL", "SZL - Swazi Lilangeni "),
    ("THB", "THB - Thai Baht "),
    ("TJS", "TJS - Tajikistani Somoni "),
    ("TMT", "TMT - Turkmenistani Manat "),
    ("TND", "TND - Tunisian Dinar "),
    ("TOP", "TOP - Tongan Paʻanga "),
    ("TRY", "TRY - Turkish Lira "),
    ("TTD", "TTD - Trinidad and Tobago Dollar "),
    ("TWD", "TWD - New Taiwan Dollar "),
    ("TZS", "TZS - Tanzanian Shilling "),
    ("UAH", "UAH - Ukrainian Hryvnia "),
    ("UGX", "UGX - Ugandan Shilling "),
    ("USDC", "USDC - Circle USD Coin "),
    ("UYU", "UYU - Uruguayan Peso "),
    ("UZS", "UZS - Uzbekistan Som "),
    ("VEF", "VEF - Venezuelan Bolívar Fuerte "),
    ("VES", "VES - Venezuelan Bolívar Soberano "),
    ("VND", "VND - Vietnamese Dong "),
    ("VUV", "VUV - Vanuatu Vatu "),
    ("WST", "WST - Samoan Tala "),
    ("XAF", "XAF - CFA Franc BEAC "),
    ("XCD", "XCD - East Caribbean Dollar "),
    ("XOF", "XOF - CFA Franc BCEAO "),
    ("XPF", "XPF - CFP Franc "),
    ("YER", "YER - Yemeni Rial "),
    ("ZAR", "ZAR - South African Rand "),
    ("ZMW", "ZMW - Zambian Kwacha "),
    ("ZWL", "ZWL - Zimbabwean Dollar "),
    ("XAG", "XAG - Silver (troy ounce) "),
    ("XAU", "XAU - Gold (troy ounce) ")
)

DELIVERY = (
    ("email", _('Email')),
    ("url", _('Url')),
)

def get_default_uuid():
    return uuid.uuid4().hex

class EmailBill(models.Model):
    uuid = models.CharField(max_length=32, editable=False, null=False,
                            blank=False, unique=True, default=get_default_uuid)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, verbose_name=_('User'), on_delete=models.deletion.CASCADE)
    currency = models.CharField(_("currency"), default="BTC", max_length=256, blank=True, choices=CURRENCY)
    email = models.CharField(_("email address"), null=True, blank=True, max_length=1000)
    cc_email = models.CharField(_("cc_ email address"), null=True, blank=True, max_length=1000)
    info = models.BooleanField(null=False, blank=False, default=False)
    name = models.TextField(_('Buyer Name'), max_length=400, blank=True)
    address = models.TextField(_('Address'), max_length=400, blank=True)
    delivery = models.CharField(max_length=30, blank=True, verbose_name=_("delivery"), choices=DELIVERY)
    country = CountryField( blank=True, verbose_name=_("country") )
    city = models.CharField(max_length=200, blank=True, verbose_name=_("city"))
    region = models.CharField(max_length=200, blank=True, verbose_name=_("region"))
    post_code = models.CharField(max_length=200, blank=True, verbose_name=_("post code"))
    recurring = models.BooleanField(null=False, blank=False, default=False)
    bill_number = models.CharField(max_length=200, blank=True, verbose_name=_("bill number"))
    processing_fee = models.BooleanField(null=False, blank=False, default=False)
    due_date = models.DateField(auto_now=True,verbose_name=_("due date"), blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        ordering = ["-created_date"]

    def duplicate(self):
        kwargs = {}
        for field in self._meta.fields:
            kwargs[field.name] = getattr(self, field.name)
            # or self.__dict__[field.name]
        kwargs.pop('id')
        kwargs.pop('uuid')
        kwargs.pop('due_date')
        kwargs.pop('created_date')
        kwargs.pop('modified_date')
        kwargs.pop('recurring')
        new_instance = self.__class__(**kwargs)
        new_instance.save()
        # now you have id for the new instance so you can
        # create related models in similar fashion
        fkey_qs = self.billitems
        new_fkeys = []
        for fkey in fkey_qs:
            fkey_kwargs = {}
            for field in fkey._meta.fields:
                fkey_kwargs[field.name] = getattr(fkey, field.name)
            fkey_kwargs.pop('id')
            fkey_kwargs.pop('created_date')
            fkey_kwargs.pop('modified_date')
            fkey_kwargs['bill'] = new_instance
            new_fkeys.append(fkey_qs.model(**fkey_kwargs))
        fkey_qs.model.objects.bulk_create(new_fkeys)
        return new_instance

    @property
    def emaillist(self):
        return eval(self.email)

    @property
    def ccemaillist(self):
        if self.cc_email:
            return eval(self.cc_email)
        else:
            return []

    @property
    def amount(self):
        items = EmailItem.objects.filter(bill=self)
        total = 0
        for item in items:
            total += (item.price * item.quantity)

        if self.processing_fee:
            total += (total*0.01)

        return round(total, 8)

    @property
    def processing_fee_total(self):
        items = EmailItem.objects.filter(bill=self)
        total = 0
        for item in items:
            total += (item.price * item.quantity)

        if self.processing_fee:
            fee = total*0.01

        return round(fee, 8)

    @property
    def billitems(self):
        return EmailItem.objects.filter(bill=self)

    @property
    def scheduledbill(self):
        bill = EmailBillScheduler.objects.filter(bill=self)
        if bill.count() > 0:
            return bill[0]
        else:
            return None

class EmailBillScheduler(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, verbose_name=_('User'), on_delete=models.deletion.CASCADE)
    bill = models.ForeignKey(EmailBill, null=False, blank=False, verbose_name=_('Email Bill'), on_delete=models.deletion.CASCADE)
    periodic_task = models.ForeignKey(PeriodicTask,related_name="periodic_task", null=True, blank=True, on_delete=models.deletion.CASCADE)
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    @staticmethod
    def schedule_every(owner, bill, task_name, period, start_time, args=None, kwargs=None):
        """ schedules a task by name every "every" "period". So an example call would be:
        TaskScheduler('mycustomtask', 'seconds', 30, [1,2,3])
        that would schedule your custom task to run every 30 seconds with the arguments 1,2 and 3 passed to the actual task.
        """
        permissible_periods = ['week', 'month', 'quarter', 'year']
        if period not in permissible_periods:
            raise Exception('Invalid period specified')
        print(period)
        if period == 'week':
            interval = 7
        elif period == 'month':
            interval = 30
        elif period == 'quarter':
            interval = 30 * 4
        else:
            interval = 365

        # create the periodic task and the interval
        ptask_name = "%s_%s" % (task_name, datetime.now()) # create some name for the period task
        schedule, _ = IntervalSchedule.objects.get_or_create(
             period='days',
             every=interval
        )

        ptask = PeriodicTask(name=ptask_name, task=task_name, interval=schedule, start_time=start_time)
        if args:
            ptask.args = bill.id
        if kwargs:
            ptask.kwargs = bill.id
        ptask.save()

        model = EmailBillScheduler(owner=owner, bill=bill,periodic_task=ptask)
        model.save()

    def stop(self):
        """pauses the task"""
        ptask = self.periodic_task
        ptask.enabled = False
        ptask.save()

    def start(self):
        """starts the task"""
        ptask = self.periodic_task
        ptask.enabled = True
        ptask.save()

    def terminate(self):
        self.stop()
        ptask = self.periodic_task
        self.delete()
        ptask.delete()

    def get_status(self):
        return self.periodic_task.enabled

class EmailItem(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, verbose_name=_('User'), on_delete=models.deletion.CASCADE)
    bill = models.ForeignKey(EmailBill, null=False, blank=False, verbose_name=_('Email Bill'), on_delete=models.deletion.CASCADE)
    name = models.CharField(_("Name of Item"), blank=True, null=True, max_length=1000)
    quantity = models.IntegerField(_("Quantity"), default=0)
    price = models.FloatField(_("Price"), default=0)
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        ordering = ["created_date"]

    @property
    def amount(self):
        return round(self.price * self.quantity, 8)

class Button(models.Model):
    uuid = models.CharField(max_length=32, editable=False, null=False, blank=False, unique=True, default=get_default_uuid)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, null=False, blank=False, verbose_name=_('User'), on_delete=models.deletion.CASCADE)
    price = models.FloatField(_("Default Price"), default=0)
    description = models.CharField(_("Description"), blank=True, default="", null=True, max_length=1000)
    currency = models.CharField(_("currency"), default="BTC", max_length=256, blank=True, choices=CURRENCY)
    ipn = models.URLField(_("ipn"), max_length=2560, blank=True)
    redirect = models.URLField(_("browser redirect"), max_length=2560, blank=True)
    width = models.IntegerField(_("width"), default=210)
    height = models.IntegerField(_("height"), default=82)
    email = models.EmailField(_("email address notification"), default="", null=True, blank=True, max_length=1000)
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        ordering = ["created_date"]

    @property
    def emaillist(self):
        return eval(self.email)

    def render(self):
        result = get_template('payment/tools/button-form.html').render({
            'uuid': self.uuid,
            'width': self.width,
            'height': self.height
        })
        return mark_safe(result)

    def escape(self):
        result = get_template('payment/tools/button-form.html').render({
            'uuid': self.uuid,
            'width': self.width,
            'height': self.height
        })
        return escape(result)

def create_user_button(sender, instance, created, **kwargs):
    if created:
        Button.objects.create(owner=instance)

def save_user_button(sender, instance, **kwargs):
    if getattr(instance,'button', None) is not None:
        instance.button.save()

post_save.connect(create_user_button, sender=settings.AUTH_USER_MODEL)
post_save.connect(save_user_button, sender=settings.AUTH_USER_MODEL)

class Checkout(models.Model):
    uuid = models.CharField(max_length=32, editable=False, null=False, blank=False, unique=True, default=get_default_uuid)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, null=False, blank=False, verbose_name=_('User'), on_delete=models.deletion.CASCADE)
    currency = models.CharField(_("currency"), default="BTC", max_length=256, blank=True, choices=CURRENCY)
    ipn = models.URLField(_("ipn"), max_length=2560, blank=True)
    email = models.EmailField(_("email address notification"), default="", null=True, blank=True, max_length=1000)
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        ordering = ["created_date"]

    @property
    def emaillist(self):
        return eval(self.email)

def create_user_checkout(sender, instance, created, **kwargs):
    if created:
        Checkout.objects.create(owner=instance)

def save_user_checkout(sender, instance, **kwargs):
    if getattr(instance,'checkout', None) is not None:
        instance.checkout.save()

post_save.connect(create_user_checkout, sender=settings.AUTH_USER_MODEL)
post_save.connect(save_user_checkout, sender=settings.AUTH_USER_MODEL)

class Buyer(models.Model):
    invoice = models.ForeignKey("payment.Invoice", null=True, blank=True, verbose_name=_('Invoice'), on_delete=models.deletion.CASCADE)
    name = models.CharField(_("Names of Buyer"), default="", blank=True, null=True, max_length=1000)
    address1 = models.TextField(_('Shipping Address 1'), default="", max_length=400, blank=True, null=True)
    address2 = models.TextField(_('Shipping Address 2'), default="", max_length=400, blank=True, null=True)
    locality = models.CharField(max_length=200, default="", blank=True, verbose_name=_("city"), null=True)
    region = models.CharField(max_length=200, default="", blank=True, verbose_name=_("region"), null=True)
    post_code = models.CharField(max_length=200, default="", blank=True, verbose_name=_("post code"), null=True)
    country = CountryField( blank=True, verbose_name=_("country") )
    phone = models.CharField(_('phone number'), default="", max_length=200, validators=[
        RegexValidator(re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}"), _('Only numbers are allowed in format 000-000-000-000'), 'invalid')
    ], blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))

    class Meta:
        ordering = ["created_date"]

class Invoice(models.Model):
    uuid = models.CharField(max_length=32, editable=False, null=False,
                            blank=False, unique=True, default=get_default_uuid)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, verbose_name=_('User'), on_delete=models.deletion.CASCADE)
    creator = models.CharField(_("creator"), default="", null=True, blank=True, max_length=1000)
    tip = models.IntegerField(_("tip"), default=0, null=True, blank=True)
    refund = models.CharField(_('refund policy'), default=CURRENT, choices=REFUND, max_length=30)
    extra = HStoreField(default=dict)
    notify = HStoreField(default=dict)
    invoice_time = models.DateTimeField(verbose_name=_('monitoring Date'))
    expiration_time = models.DateTimeField(verbose_name=_('expiration Date'))
    current_time = models.DateTimeField(verbose_name=_('current Date'))
    content_type = models.ForeignKey(ContentType, null=True, blank=True,
                                     verbose_name=_("content type"), on_delete=models.deletion.PROTECT)
    object_id = models.PositiveIntegerField(null=True, blank=True,
                                            verbose_name=_("object id"))
    content_object = GenericForeignKey("content_type", "object_id")
    redirect_url = models.URLField(_("redirect url"), max_length=2560, blank=True)
    notification_url = models.URLField(_("notification url"), max_length=2560, blank=True)
    notification_email = models.EmailField(_("email address"), default="", null=True, blank=True, max_length=1000)

    class Meta:
        ordering = ["-current_time"]

    def has_expired(self):
        if datetime.timestamp(self.expiration_time) < datetime.timestamp(datetime.now()):
            return True
        return False

    def get_invoice_update(self):
        client = PesaifyClient(
            host=settings.BITCOIN_URL,
            pem=settings.PRIVKEY,
            tokens={'merchant': settings.MERCHANT}
        )
        self.extra = client.get_invoice(self.uuid)
        self.save()

class AfricaCountries(Countries):
    only = [
        'UG', 'KE', 'TZ',
    ]

class MobileMoneySettlement(models.Model):
    invoice = models.ForeignKey(Invoice, null=True, blank=True, verbose_name=_('Invoice'), on_delete=models.deletion.CASCADE)
    currency = models.CharField(_("currency"), default="MM", max_length=256, blank=False, choices=MM_CURRENCY)
    phone_number = models.CharField(_('phone number'), max_length=200, validators=[
        RegexValidator(re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}"), _('Only numbers are allowed in format 000-000-000-000'), 'invalid')
    ], blank=False)
    country = CountryField( blank=True, verbose_name=_("country"), countries=AfricaCountries)
    label = models.CharField(max_length=100, blank=False, default="", verbose_name=_("label"))
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        ordering = ["-created_date"]

class CryptoSettlement(models.Model):
    invoice = models.ForeignKey(Invoice, null=True, blank=True, verbose_name=_('Invoice'), on_delete=models.deletion.CASCADE)
    currency = models.CharField(_("currency"), default="BTC", max_length=256, blank=True, choices=CRYPTO_CURRENCY)
    address = models.CharField(max_length=100, null=True, blank=False)
    label = models.CharField(max_length=100, blank=True, default="", verbose_name=_("label"))
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        ordering = ["-created_date"]

class BankSettlement(models.Model):
    invoice = models.ForeignKey(Invoice, null=True, blank=True, verbose_name=_('Invoice'), on_delete=models.deletion.CASCADE)
    currency = models.CharField(_("currency"), default="USD" ,max_length=256, blank=False, choices=BANK_CURRENCY)
    name = models.CharField(max_length=100, null=True, blank=False)
    address = models.CharField(max_length=100, null=True, blank=False)
    city = models.CharField(max_length=100, null=True, blank=False)
    address = models.CharField(max_length=100, null=True, blank=False)
    country = CountryField( blank=True, verbose_name=_("country"))
    post_code = models.CharField(_("post code"), max_length=256, blank=False, default="")
    account_name = models.CharField(max_length=100, null=True, blank=False)
    account_number = models.CharField(max_length=100, null=True, blank=False)
    swift_bic = models.CharField(max_length=100, null=True, blank=False)
    label = models.CharField(max_length=100, blank=True, default="", verbose_name=_("label"))
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        ordering = ["-created_date"]
