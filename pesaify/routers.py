# -*- coding: utf-8 -*-
from rest_framework import routers
from django.conf import settings

if settings.DEBUG:
    router = routers.DefaultRouter()
else:
    router = routers.SimpleRouter()

# Root
from .api import PesaifyViewSet

router.register(r"", PesaifyViewSet, base_name="pesaify")

# Users
from pesaify.users.api import UsersViewSet

router.register(r"api/v1/users", UsersViewSet, base_name="users")

from pesaify.users.api import BusinessViewSet

router.register(r"api/v1/business", BusinessViewSet, base_name="business")

# Settlement
from pesaify.users.api import MobileMoneySettlementViewSet
from pesaify.users.api import CryptoSettlementViewSet
from pesaify.users.api import BankSettlementViewSet

router.register(r"api/v1/mobile-money", MobileMoneySettlementViewSet, base_name="mobile-money")
router.register(r"api/v1/crypto-currency", CryptoSettlementViewSet, base_name="crypto-currency")
router.register(r"api/v1/bank", BankSettlementViewSet, base_name="bank")

# Payment Tools
from pesaify.payment.api import EmailItemViewSet

router.register(r"api/v1/email-item", EmailItemViewSet, base_name="email-item")

from pesaify.payment.api import EmailBillViewSet

router.register(r"api/v1/email-bill", EmailBillViewSet, base_name="email-bill")

from pesaify.payment.api import ButtonViewSet

router.register(r"api/v1/button", ButtonViewSet, base_name="button")

from pesaify.payment.api import CheckoutViewSet

router.register(r"api/v1/checkout", CheckoutViewSet, base_name="checkout")

from pesaify.payment.api import InvoiceViewSet

router.register(r"api/v1/invoice", InvoiceViewSet, base_name="invoice")
