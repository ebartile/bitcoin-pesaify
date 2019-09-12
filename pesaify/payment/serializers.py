from rest_framework import serializers
from .models import EmailItem, EmailBill, Button, Checkout, CURRENCY, Invoice
from pesaify.base.templatetags.functions import resolve
from django.core import validators
from pesaify.base import exceptions as exc
from django_countries.serializers import CountryFieldMixin
from rest_pandas.serializers import PandasSerializer

class EmailBillUpdateSerializer(CountryFieldMixin, serializers.ModelSerializer):

    class Meta:
        model = EmailBill
        fields = ("name","address", "country", "city", "region", "post_code",)

class EmailBillSerializer(CountryFieldMixin, serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = EmailBill
        fields = '__all__'
        read_only_fields = ("owner",)

    def validate_cc_email(self,value):
        ccemails = eval(value)
        for x in ccemails:
            validators.validate_email(x)
        return value

    def validate_email(self,value):
        emails = eval(value)
        for x in emails:
            validators.validate_email(x)
        return value

    def get_url(self, obj):
        return resolve('pesaify-invoice-email', obj.uuid)

class EmailItemsSerializer(serializers.ModelSerializer):
    bill = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = EmailItem
        fields = '__all__'
        read_only_fields = ("owner",'bill',)

    def get_amount(self, obj):
        return obj.price * obj.quantity

    def get_bill(self, obj):
        return EmailBillSerializer(obj).data

class ButtonSerializer(serializers.ModelSerializer):
    render = serializers.SerializerMethodField()
    escape = serializers.SerializerMethodField()

    class Meta:
        model = Button
        fields = '__all__'
        read_only_fields = ("uuid","owner",)

    def get_render(self, obj):
        return obj.render()

    def get_escape(self, obj):
        return obj.escape()

class CheckoutSerializer(serializers.ModelSerializer):

    class Meta:
        model = Checkout
        fields = '__all__'
        read_only_fields = ("uuid","owner",)

class InvoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        fields = '__all__'
