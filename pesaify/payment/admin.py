# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import (Invoice, Checkout, Button, EmailBill, EmailBillScheduler, EmailItem, CryptoSettlement, BankSettlement, MobileMoneySettlement, Buyer)

class BuyerInline(admin.TabularInline):
    model = Buyer
    extra = 0

class MobileMoneySettlementInline(admin.TabularInline):
    model = MobileMoneySettlement
    extra = 0

class BankSettlementInline(admin.TabularInline):
    model = BankSettlement
    extra = 0

class CryptoSettlementInline(admin.TabularInline):
    model = CryptoSettlement
    extra = 0

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["owner", "uuid", "current_time", "content_type",]
    list_display_links = ["uuid",]
    search_fields = ["uuid", "owner__username", "owner__email",]
    inlines = [
               MobileMoneySettlementInline,
               BankSettlementInline,
               CryptoSettlementInline,
               BuyerInline
               ]

class CheckoutAdmin(admin.ModelAdmin):
    list_display = ("owner",'currency','modified_date',)
    search_fields = ['owner__username','currency',]

class ButtonAdmin(admin.ModelAdmin):
    list_display = ("owner",'currency','description','modified_date',)
    search_fields = ['owner__username','currency',]

class EmailItemAdmin(admin.ModelAdmin):
    list_display = ("owner",'bill','name','price','quantity','modified_date',)
    search_fields = ['owner__username','name',]

class EmailBillAdmin(admin.ModelAdmin):
    list_display = ("owner",'email','currency','modified_date',)
    search_fields = ['owner__username','email','currency']

class EmailBillSchedulerAdmin(admin.ModelAdmin):
    list_display = ("owner",'bill','modified_date',)
    search_fields = ['owner__username']

admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Checkout, CheckoutAdmin)
admin.site.register(Button, ButtonAdmin)
admin.site.register(EmailBillScheduler, EmailBillSchedulerAdmin)
admin.site.register(EmailItem, EmailItemAdmin)
admin.site.register(EmailBill, EmailBillAdmin)
