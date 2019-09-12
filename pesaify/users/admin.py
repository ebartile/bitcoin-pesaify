# -*- coding: utf-8 -*-
from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User, Business, CryptoSettlement, BankSettlement, MobileMoneySettlement
from .forms import UserChangeForm, UserCreationForm
admin.site.unregister(Group)

## Inlines


## Admin panels
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ('first_name', 'middle_name', 'last_name',
                                         "email", "bio", "photo", "passport",
                                         "permit_id_front", "permit_id_back",
                                         "photo_recording", "passport_recording",
                                         "permit_id_front_recording", "permit_id_back_recording",
                                         "message", "dismiss_message",)}),
        (_("Extra info"), {"fields": ( 'country_document', 'document_type', "nationality",
                                       "city", "region", "date_of_birth", 'address','address_two',
                                       "lang", "timezone", "token", 'unit_system',
                                       "email_token", "new_email","accepted_terms", "read_new_terms",)}),
        (_("Permissions"), {"fields": ("is_active", "is_superuser","is_staff","is_verified",)}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("username", "email", 'first_name', 'middle_name', 'last_name',)
    list_filter = ("is_superuser", "is_active","is_staff","is_verified")
    search_fields = ("username", 'first_name', 'middle_name', 'last_name', "email")
    ordering = ("username",)
    filter_horizontal = ()

class MobileMoneySettlementInline(admin.TabularInline):
    model = MobileMoneySettlement
    extra = 0

class BankSettlementInline(admin.TabularInline):
    model = BankSettlement
    extra = 0

class CryptoSettlementInline(admin.TabularInline):
    model = CryptoSettlement
    extra = 0

class BusinessAdmin(admin.ModelAdmin):
    list_display = ("owner",'legal_name', 'tier0','tier1','tier2','industry_name','modified_date',)
    search_fields = ['industry_name','tier0','tier1','tier2', "owner__username", "owner__email", "owner__full_name"]
    inlines = [
               MobileMoneySettlementInline,
               BankSettlementInline,
               CryptoSettlementInline
               ]

admin.site.register(Business, BusinessAdmin)
admin.site.register(User, UserAdmin)
