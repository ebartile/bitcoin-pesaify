# -*- coding: utf-8 -*-
import uuid
import re
from django.shortcuts import reverse
from django_countries import Countries
from django_countries.fields import CountryField
from django.db.models import Sum
from djmoney.models.fields import MoneyField
from moneyed import USD, Money
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils import six
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.db.models.signals import post_save, pre_save
from django.core.validators import RegexValidator
from django_pglocks import advisory_lock

from pesaify.base.db.models.fields import JSONField
from pesaify.base.utils.slug import slugify_uniquely
from pesaify.base.utils.files import get_file_path
from pesaify.base.utils.time import timestamp_ms
from pesaify.base.tokens import get_token_for_user
from pesaify.base.mails import mail_builder

from django.dispatch import receiver
from two_factor.signals import user_verified
from pesaify.payment.models import EmailBill, Invoice
from django.db.models import signals
from django.core.mail import send_mail
from .services import get_user_photo_url, get_user_big_photo_url, get_user_passport_url, get_user_big_passport_url, get_user_permit_id_front_url,get_user_big_permit_id_front_url, get_user_permit_id_back_url, get_user_big_permit_id_back_url

def get_business_proof_of_address_file_path(instance, filename):
    return get_file_path(instance, filename, "business/proof_of_address")

def get_business_owner_photo_file_path(instance, filename):
    return get_file_path(instance, filename, "business/owner_photo")

def get_business_documents_file_path(instance, filename):
    return get_file_path(instance, filename, "business/documents")

def get_user_photo_file_path(instance, filename):
    return get_file_path(instance, filename, "user/photo")

def get_user_photo_recording_file_path(instance, filename):
    return get_file_path(instance, filename, "user/photo/recording")

def get_user_passport_file_path(instance, filename):
    return get_file_path(instance, filename, "user/passport")

def get_user_passport_recording_file_path(instance, filename):
    return get_file_path(instance, filename, "user/passport/recording")

def get_user_permit_id_front_file_path(instance, filename):
    return get_file_path(instance, filename, "user/permit_id/front")

def get_user_permit_id_front_recording_file_path(instance, filename):
    return get_file_path(instance, filename, "user/permit_id/front/recording")

def get_user_permit_id_back_file_path(instance, filename):
    return get_file_path(instance, filename, "user/permit_id/back")

def get_user_permit_id_back_recording_file_path(instance, filename):
    return get_file_path(instance, filename, "user/permit_id/back/recording")

SUCCESSFULL = "Successfull"
FAILED = "Failed"
STATUS = (
    (SUCCESSFULL, _("Successful login")),
    (FAILED, _("Failed attempt"))
)

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

PENDING = '1'
VERIFIED = '3'
UNVERIFIED = '2'
REVIEW = '4'

STATUS = (
    (UNVERIFIED, 'UnVerified'),
    (PENDING, 'Pending'),
    (VERIFIED, 'Verified'),
    (REVIEW, 'Under Review'),
)
HIGH = '1'
MEDIUM = '2'
LOW = '3'

SPEED = (
    (HIGH, 'High'),
    (MEDIUM, 'Medium'),
    (LOW, 'Low')
)

CURRENT = 'Current'
FIXED = 'Fixed'

REFUND = (
    (CURRENT, 'Current'),
    (FIXED, 'Fixed')
)

PASSPORT = "Passport"
PERMIT_OR_ID = "Permit Or National ID"
DOCUMENT_TYPE = (
    (PASSPORT, _('Passport')),
    (PERMIT_OR_ID, _('Permit Or National ID')),
)

def get_default_uuid_hex():
    return uuid.uuid4()

def get_default_uuid():
    return uuid.uuid4().hex

class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.CharField(max_length=32, editable=False, null=False,
                            blank=False, unique=True, default=get_default_uuid)
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        default=get_default_uuid_hex,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), max_length=255, blank=True, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_email_verified = models.BooleanField(_('email verified'), default=False,
                                      help_text=_('Designates whether the user email is a veriyfied user'))
    is_verified = models.CharField(_('is verified'), default=UNVERIFIED, choices=STATUS,
                                       max_length=30, help_text=_('Designates whether the settlement is a verified'))
    is_active = models.BooleanField(_("active"), default=True,
        help_text=_("Designates whether this user should be treated as "
                    "active. Unselect this instead of deleting accounts."))
    short_name = models.CharField(_('short name'), max_length=30, blank=True)
    sex = models.CharField(_('sex'), max_length=30, blank=True, default="",
        choices=(('Male', 'Male'), ('Female', 'Female'),('Other', 'other')))
    phone_number = models.CharField(_('phone number'), max_length=200, validators=[
        RegexValidator(re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}"), _('Only numbers are allowed in format 000-000-000-000'), 'invalid')
    ], blank=True)
    address = models.TextField(_('Address'), max_length=400, blank=True)
    address_two = models.TextField(_('Second Address'), max_length=400, blank=True)
    first_name = models.CharField(_("first name"), max_length=256, blank=True)
    middle_name = models.CharField(_("middle name"), max_length=256, blank=True)
    last_name = models.CharField(_("last name"), max_length=256, blank=True)
    bio = models.TextField(blank=True, verbose_name=_("biography"))
    message = models.TextField(blank=True, verbose_name=_("Custom Message"))
    dismiss_message = models.BooleanField(_("Dismiss message"), default=False)
    photo = models.ImageField(upload_to=get_user_photo_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("photo"))
    photo_recording = models.ImageField(upload_to=get_user_photo_recording_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("photo recording"))
    passport = models.ImageField(upload_to=get_user_passport_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("passport"))
    passport_recording = models.ImageField(upload_to=get_user_passport_recording_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("passport recording"))
    permit_id_front = models.ImageField(upload_to=get_user_permit_id_front_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("permit / National ID Front"))
    permit_id_front_recording = models.ImageField(
                             upload_to=get_user_permit_id_front_recording_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("permit / National ID Front Recording"))
    permit_id_back = models.ImageField(upload_to=get_user_permit_id_back_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("permit / National ID Back"))
    permit_id_back_recording = models.ImageField(
                             upload_to=get_user_permit_id_back_recording_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("permit / National ID Back Recording"))
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    accepted_terms = models.BooleanField(_("accepted terms"), default=False)
    read_new_terms = models.BooleanField(_("new terms read"), default=False)
    lang = models.CharField(max_length=200, blank=True, default="en",
                            verbose_name=_("default language"),choices=settings.LANGUAGES)
    city = models.CharField(max_length=200, blank=True, verbose_name=_("city"))
    region = models.CharField(max_length=200, blank=True, verbose_name=_("region"))
    nationality = CountryField( blank=True, verbose_name=_("nationality") )
    country_document = CountryField( blank=True, verbose_name=_("country") )
    document_type = models.CharField(max_length=30, blank=True,
                            verbose_name=_("document type"), choices=DOCUMENT_TYPE, default=PASSPORT)
    date_of_birth = models.DateField(verbose_name=_("date of birth"), blank=True, null=True)
    timezone = models.CharField(max_length=200, blank=True, default="UTC",
                                verbose_name=_("default timezone"))
    token = models.CharField(max_length=2000, null=True, blank=True, default=None,
                             verbose_name=_("token"))
    email_token = models.CharField(max_length=2000, null=True, blank=True, default=None,
                         verbose_name=_("email token"))
    new_email = models.EmailField(_("new email address"), null=True, blank=True)
    is_system = models.BooleanField(null=False, blank=False, default=False)
    unit_system  = models.CharField(max_length=2000, blank=True, default="",
                         verbose_name=_("unit system"))

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["username"]

    def __str__(self):
        return self.get_full_name()

    def get_photo(self):
        return get_user_photo_url(self)

    def get_big_photo(self):
        return get_user_big_photo_url(self)

    def get_passport(self):
        return get_user_passport_url(self)

    def get_big_passport(self):
        return get_user_big_passport_url(self)

    def get_permit_id_front(self):
        return get_user_permit_id_front_url(self)

    def get_big_permit_id_front(self):
        return get_user_big_permit_id_front_url(self)

    def get_permit_id_back(self):
        return get_user_permit_id_back_url(self)

    def get_big_permit_id_back(self):
        return get_user_big_permit_id_back_url(self)

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name or self.username

    def get_full_name(self):
        return "{0} {1} {2}".format(self.first_name, self.middle_name, self.last_name)  or self.username or self.email

    @property
    def balance(self):
        balance = 0
        invoices = Invoice.objects.filter(owner=self, extra__status="complete")
        for invoice in invoices:
            balance += float(invoice.extra['btcPaid'])

        return "{}{}".format("BTC", balance)

    @property
    def emailbills(self):
        return EmailBill.objects.filter(owner=self)

    @property
    def mobilemoneysettlement(self):
        return MobileMoneySettlement.objects.filter(owner=self)

    @property
    def mobilemoneysettlementreview(self):
        return MobileMoneySettlement.objects.filter(owner=self, is_verified=REVIEW)

    @property
    def mobilemoneysettlementpending(self):
        return MobileMoneySettlement.objects.filter(owner=self, is_verified=PENDING)

    @property
    def mobilemoneysettlementunverified(self):
        return MobileMoneySettlement.objects.filter(owner=self, is_verified=UNVERIFIED)

    @property
    def mobilemoneysettlementverified(self):
        return MobileMoneySettlement.objects.filter(owner=self, is_verified=VERIFIED)

    @property
    def cryptosettlement(self):
        return CryptoSettlement.objects.filter(owner=self)

    @property
    def cryptosettlementpending(self):
        return CryptoSettlement.objects.filter(owner=self, is_verified=PENDING)

    @property
    def cryptosettlementreview(self):
        return CryptoSettlement.objects.filter(owner=self, is_verified=REVIEW)

    @property
    def cryptosettlementunverified(self):
        return CryptoSettlement.objects.filter(owner=self, is_verified=UNVERIFIED)

    @property
    def cryptosettlementverified(self):
        return CryptoSettlement.objects.filter(owner=self, is_verified=VERIFIED)

    @property
    def banksettlement(self):
        return BankSettlement.objects.filter(owner=self)

    @property
    def banksettlementpending(self):
        return BankSettlement.objects.filter(owner=self, is_verified=PENDING)

    @property
    def banksettlementreview(self):
        return BankSettlement.objects.filter(owner=self, is_verified=REVIEW)

    @property
    def banksettlementunverified(self):
        return BankSettlement.objects.filter(owner=self, is_verified=UNVERIFIED)

    @property
    def banksettlementverified(self):
        return BankSettlement.objects.filter(owner=self, is_verified=VERIFIED)

    @property
    def settlements(self):
        settlements = [settlement for settlement in self.cryptosettlement] + [settlement for settlement in self.mobilemoneysettlement] + [settlement for settlement in self.banksettlement]
        if len(settlements) > 0:
            return settlements
        else:
            return []

    def save(self, *args, **kwargs):
        get_token_for_user(self, "cancel_account")
        super().save(*args, **kwargs)

    def cancel(self):
        with advisory_lock("delete-user"):
            deleted_user_prefix = "{0}-deleted-user-{1}".format(self.username,timestamp_ms())
            self.username = slugify_uniquely(deleted_user_prefix, User, slugfield="username")
            self.email = "{}.cancel".format(self.email)
            self.is_active = False
            self.token = None
            self.save()

class Business(models.Model):
    owner = models.OneToOneField(User, null=False, blank=False, verbose_name=_('User'), on_delete=models.deletion.CASCADE)
    daily_maximum = MoneyField(default=Money(0, USD),max_digits=12, decimal_places=2, verbose_name=_('Daily Maximum'))
    annual_maximum = MoneyField(default=Money(0, USD),max_digits=12, decimal_places=2, verbose_name=_('Annual Maximum'))
    notify = models.BooleanField(_('notify'), default=True)
    refund = models.CharField(_('refund policy'), default=CURRENT, choices=REFUND, max_length=30)
    tier0 = models.CharField(_('teir 0 verified'), default=UNVERIFIED, choices=STATUS,
                                       max_length=30, help_text=_('Designates whether the business is a verified'))
    tier1 = models.CharField(_('teir 1 verified'), default=UNVERIFIED, choices=STATUS,
                                       max_length=30, help_text=_('Designates whether the business is a verified'))
    tier2 = models.CharField(_('teir 2 verified'), default=UNVERIFIED, choices=STATUS,
                                       max_length=30, help_text=_('Designates whether the business is a verified'))
    legal_name = models.CharField(_('legal name'), max_length=30, blank=True)
    industry_name = models.CharField(_('Industry'), max_length=30, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=200, validators=[
        RegexValidator(re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}"), _('Only numbers are allowed in format 000-000-000-000'), 'invalid')
    ], blank=True)
    street_number = models.TextField(_('Street Number'), max_length=400, blank=True)
    street_name = models.TextField(_('Street Name'), max_length=400, blank=True)
    unit = models.TextField(_('Unit'), max_length=400, blank=True)
    city = models.CharField(max_length=200, blank=True, verbose_name=_("city"))
    region = models.CharField(max_length=200, blank=True, verbose_name=_("region"))
    documents = models.ImageField(upload_to=get_business_documents_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("documents"))
    owner_photo = models.ImageField(upload_to=get_business_owner_photo_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("documents"))
    proof_of_address = models.ImageField(upload_to=get_business_proof_of_address_file_path,
                             max_length=500, null=True, blank=True,
                             verbose_name=_("proof of address"))
    tin = models.CharField(max_length=30, blank=True, verbose_name=_("tax id number"))
    country = CountryField( blank=True, verbose_name=_("country") )
    website = models.URLField(max_length=2000, blank=True, verbose_name=_("webiste"))
    owner_first_name = models.CharField(_("owner first name"), max_length=256, blank=True)
    owner_middle_name = models.CharField(_("owner middle name"), max_length=256, blank=True)
    owner_last_name = models.CharField(_("owner last name"), max_length=256, blank=True)
    owner_date_of_birth = models.DateField(verbose_name=_("owner date of birth"), blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        verbose_name = "business"
        verbose_name_plural = "businesses"
        ordering = ["-created_date"]

def create_user_business(sender, instance, created, **kwargs):
    if created:
        Business.objects.create(owner=instance)

def save_user_business(sender, instance, **kwargs):
    if getattr(instance,'business', None) is not None:
        instance.business.save()

post_save.connect(create_user_business, sender=settings.AUTH_USER_MODEL)
post_save.connect(save_user_business, sender=settings.AUTH_USER_MODEL)

class AfricaCountries(Countries):
    only = [
        'UG', 'KE', 'TZ',
    ]

class MobileMoneySettlement(models.Model):
    business = models.ForeignKey(Business, null=False, blank=False, verbose_name=_('Business'), on_delete=models.deletion.CASCADE)
    owner = models.ForeignKey(User, null=False, blank=False, verbose_name=_('User'), on_delete=models.deletion.CASCADE)
    is_verified = models.CharField(_('is verified'), default=UNVERIFIED, choices=STATUS,
                                       max_length=30, help_text=_('Designates whether the settlement is a verified'))
    currency = models.CharField(_("currency"), default="MM", max_length=256, blank=False, choices=MM_CURRENCY)
    phone_number = models.CharField(_('phone number'), max_length=200, validators=[
        RegexValidator(re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}|\d{3}[-\.\s]??\d{3}[-\.\s]??\d{3}"), _('Only numbers are allowed in format 000-000-000-000'), 'invalid')
    ], blank=False)
    country = CountryField( blank=True, verbose_name=_("country"), countries=AfricaCountries)
    label = models.CharField(max_length=100, blank=False, default="", verbose_name=_("label"))
    token = models.CharField(max_length=2000, null=True, blank=True, default=None,verbose_name=_("token"))
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        ordering = ["-created_date"]

    def category(self):
        return "{}-{}".format("Mobile Money", self.currency)

    def url(self):
        return reverse('mobile-money-detail', args=[self.id])

    def resend_mail_url(self):
        return reverse('mobile-money-resend', args=[self.id])


class CryptoSettlement(models.Model):
    business = models.ForeignKey(Business, null=False, blank=False, verbose_name=_('Business'), on_delete=models.deletion.CASCADE)
    owner = models.ForeignKey(User, null=False, blank=False, verbose_name=_('User'), on_delete=models.deletion.CASCADE)
    is_verified = models.CharField(_('is verified'), default=UNVERIFIED, choices=STATUS,
                                       max_length=30, help_text=_('Designates whether the settlement is a verified'))
    currency = models.CharField(_("currency"), default="BTC", max_length=256, blank=True, choices=CRYPTO_CURRENCY)
    address = models.CharField(max_length=100, null=True, blank=False)
    label = models.CharField(max_length=100, blank=True, default="", verbose_name=_("label"))
    token = models.CharField(max_length=2000, null=True, blank=True, default=None,verbose_name=_("token"))
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        ordering = ["-created_date"]

    def category(self):
        return "{}-{}".format("Crypto", self.currency)

    def url(self):
        return reverse('crypto-currency-detail', args=[self.id])

    def resend_mail_url(self):
        return reverse('crypto-currency-resend', args=[self.id])

class BankSettlement(models.Model):
    business = models.ForeignKey(Business, null=False, blank=False, verbose_name=_('Business'), on_delete=models.deletion.CASCADE)
    owner = models.ForeignKey(User, null=False, blank=False, verbose_name=_('User'), on_delete=models.deletion.CASCADE)
    is_verified = models.CharField(_('is verified'), default=UNVERIFIED, choices=STATUS,
                                       max_length=30, help_text=_('Designates whether the settlement is a verified'))
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
    token = models.CharField(max_length=2000, null=True, blank=True, default=None,verbose_name=_("token"))
    created_date = models.DateTimeField(auto_now=True, verbose_name=_('Created Date'))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_('Modified Date'))

    class Meta:
        ordering = ["-created_date"]

    def category(self):
        return "{}-{}".format("Bank Account", self.currency)

    def url(self):
        return reverse('bank-detail', args=[self.id])

    def resend_mail_url(self):
        return reverse('bank-resend', args=[self.id])

@receiver(user_verified)
def two_factor_receiver(request, user, device, **kwargs):
    if device.name == 'backup':
        context = {"user": user}
        email = mail_builder.two_factor_recieved(user, context)
