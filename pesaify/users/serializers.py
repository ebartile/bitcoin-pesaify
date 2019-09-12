# -*- coding: utf-8 -*-
from collections import OrderedDict
from moneyed import Money
from rest_framework.relations import PKOnlyObject  # NOQA # isort:skip
from django_countries.serializers import CountryFieldMixin
from django.conf import settings

from rest_framework import serializers
from pesaify.base.utils.thumbnails import get_thumbnail_url

from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from .services import get_user_photo_url, get_user_big_photo_url, get_user_passport_url, get_user_big_passport_url, get_user_permit_id_front_url,get_user_big_permit_id_front_url, get_user_permit_id_back_url, get_user_big_permit_id_back_url
from django.core import validators as core_validators
from .models import User, Business, MobileMoneySettlement, BankSettlement, CryptoSettlement
from rest_framework.fields import SkipField

######################################################
# User
######################################################
class RecoveryValidator(serializers.Serializer):
    token = serializers.CharField(max_length=200)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_password(self,value):
        if value != self.initial_data.get('confirm_password', None):
            raise ValidationError(_("Passwords should match."))

        validate_password(value)

        return value

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_password(self,value):

        validate_password(value)

        return value

class PasswordRecoverySerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

class ChangeEmailValidator(serializers.Serializer):
    email_token = serializers.CharField(max_length=2000)

class CancelAccountValidator(serializers.Serializer):
    cancel_token = serializers.CharField(max_length=2000)

class ChangeAvatarSerializer(serializers.Serializer):
    avatar = serializers.FileField(required=True)
    avatar_recording = serializers.FileField(required=True)

class ChangePassportSerializer(serializers.Serializer):
    passport = serializers.FileField(required=True)
    passport_recording = serializers.FileField(required=True)

class ChangePermitIdFrontSerializer(serializers.Serializer):
    permit_id_front = serializers.FileField(required=True)
    permit_id_front_recording = serializers.FileField(required=True)

class ChangePermitIdBackSerializer(serializers.Serializer):
    permit_id_back = serializers.FileField(required=True)
    permit_id_back_recording = serializers.FileField(required=True)

######################################################
# User
######################################################

class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    big_photo = serializers.SerializerMethodField()
    passport = serializers.SerializerMethodField()
    big_passport = serializers.SerializerMethodField()
    permit_id_front = serializers.SerializerMethodField()
    big_permit_id_front = serializers.SerializerMethodField()
    permit_id_back = serializers.SerializerMethodField()
    big_permit_id_back = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'bio', 'country_document', 'document_type', 'nationality',
                  'date_of_birth', 'address', 'address_two', 'lang',
                  'timezone', 'is_active','full_name', 'first_name', 'middle_name',
                  'last_name', 'photo', 'big_photo', 'passport', 'big_passport',
                  'permit_id_front', 'big_permit_id_front', 'permit_id_back',
                  'big_permit_id_back','city', 'region','phone_number','dismiss_message','message',)
        read_only_fields = ("username","is_active",'message',)

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                if isinstance(attribute, Money):
                    attribute = attribute.amount
                ret[field.field_name] = field.to_representation(attribute)

        return ret

    def get_full_name(self, obj):
        return obj.get_full_name() if obj else ""

    def get_photo(self, user):
        return get_user_photo_url(user)

    def get_big_photo(self, user):
        return get_user_big_photo_url(user)

    def get_passport(self, user):
        return get_user_passport_url(user)

    def get_big_passport(self, user):
        return get_user_big_passport_url(user)

    def get_permit_id_front(self, user):
        return get_user_permit_id_front_url(user)

    def get_big_permit_id_front(self, user):
        return get_user_big_permit_id_front_url(user)

    def get_permit_id_back(self, user):
        return get_user_permit_id_back_url(user)

    def get_big_permit_id_back(self, user):
        return get_user_big_permit_id_back_url(user)

class UserAdminSerializer(CountryFieldMixin, serializers.ModelSerializer):

    class Meta:
        model = User
        read_only_fields = ("last_login","username","is_active","date_joined","token","photo","active","is_verified","accepted_terms",)
        exclude = ("password","is_superuser","is_staff","email_token","is_system","unit_system","new_email","user_permissions","groups",)

class UserBasicInfoSerializer(CountryFieldMixin, serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    big_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'is_active', 'first_name', 'middle_name', 'last_name', 'full_name',
        'photo', 'big_photo', )
        read_only_fields = ("username","is_active",)

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_photo(self, obj):
        return get_user_photo_url(obj)

    def get_big_photo(self, obj):
        return get_user_big_photo_url(obj)

class BaseRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',)

class PublicRegisterSerializer(BaseRegisterSerializer):
    company_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ('company_name', 'first_name', 'middle_name', 'last_name', 'password','confirm_password','accepted_terms',)

    def validate_password(self,value):
        if value != self.initial_data.get('confirm_password', None):
            raise ValidationError(_("Passwords should match."))

        validate_password(value)

        return value

    def validate_accepted_terms(self,value):
        if not value:
            raise ValidationError(_("You must accept our terms of service and privacy policy"))

        return value

######################################################
# Business
######################################################

class BusinessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = '__all__'
        read_only_fields = ("owner",'tier0','tier1','tier2','daily_maximum','annual_maximum',)

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                if isinstance(attribute, Money):
                    attribute = attribute.amount
                ret[field.field_name] = field.to_representation(attribute)

        return ret

######################################################
# Settlement
######################################################

class MobileMoneySerializer(serializers.ModelSerializer):

    class Meta:
        model = MobileMoneySettlement
        fields = '__all__'
        read_only_fields = ("owner","business","is_verified","token",)

class CryptoSettlementSerializer(serializers.ModelSerializer):

    class Meta:
        model = CryptoSettlement
        fields = '__all__'
        read_only_fields = ("owner","business","is_verified","token",)

class BankSettlementSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankSettlement
        fields = '__all__'
        read_only_fields = ("owner","business","is_verified","token",)

class ActivateSettlementValidator(serializers.Serializer):
    activation_token = serializers.CharField(max_length=2000)
