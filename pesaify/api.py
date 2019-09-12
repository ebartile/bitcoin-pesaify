import re
import requests
from datetime import datetime
from django_countries import countries
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect,reverse, get_object_or_404
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.contrib.auth import login
from pesaify.base import exceptions as exc
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth import logout
from .base.utils.qr import get_qrcode
from .base.tokens import get_user_for_token
from .users import services, api
from .users import models
from .payment.serializers import InvoiceSerializer
from .payment.models import EmailBill, Button, Checkout, Invoice, CURRENCY, Buyer
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import list_route, action
from .client import PesaifyClient
from .decorators import login_forbidden, login_required
from two_factor.utils import default_device
from django.contrib.contenttypes.models import ContentType
from pesaify.base.templatetags.functions import resolve

class PesaifyViewSet(ViewSet):

    def checks(self, request, **kwargs):
        if not request.user.is_email_verified:
            return False
        return True

    @list_route(methods=["GET"])
    @login_forbidden
    def signup(self, request, **kwargs):
        return render(request, 'signup.html', {'sitekey': settings.GOOGLE_RECAPTCHA_SITE_KEY})

    @list_route(methods=["GET"])
    def logout(self, request, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, _('You have successfully logged out!'))
        return redirect(reverse('two_factor:login'))

    @action(methods=['GET'], detail=False, url_path="forgot-password")
    @login_forbidden
    def forgot_password(self, request, **kwargs):
        return render(request, 'forgot-password.html')

    @action(methods=['GET'], detail=False, url_path="change-password")
    @login_required
    def change_password(self, request, **kwargs):
        return render(request, 'change-password.html')

    @action(methods=['GET'], detail=False, url_path="change-password-from-recovery/(?P<token>[0-9A-Za-z_\-:]+)")
    def change_password_from_recovery(self, request, token, **kwargs):
        return render(request, 'change-password-from-recovery.html', {"token":token})

    @list_route(methods=["GET"])
    @login_required
    def dashboard(self, request, **kwargs):
        if self.checks(request, **kwargs):
            return render(request, 'dashboard/index.html', {'default_device': default_device(request.user) })
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(methods=['GET'], detail=False, url_path="dashboard/setup")
    @login_required
    def dashboard_setup(self, request, **kwargs):
        return render(request, 'dashboard/setup.html')

    @action(methods=['GET'], detail=False, url_path="dashboard/get-started")
    @login_required
    def dashboard_get_started(self, request, **kwargs):
        return render(request, 'dashboard/get-started.html')

    @action(methods=['GET'], detail=False, url_path="account/update-email-address")
    @login_required
    def account_update_email_address(self, request, **kwargs):
        return render(request, 'account/update-email-address.html')

    @action(detail=False, methods=['GET'], url_path="verify-email/(?P<email_token>[0-9A-Za-z_\-:]+)")
    def account_verify_email_address(self, request, email_token, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, _('Please login to verfiy email!'))
        return render(request, 'account/verify-email-address.html', {'email_token': email_token})

    @action(detail=False, methods=['GET'], url_path="account/verification")
    @login_required
    def account_verification(self, request, **kwargs):
        return render(request, 'account/verification.html')

    @action(detail=False, methods=['GET'], url_path="account/verification/step-one")
    @login_required
    def account_verification_step_one(self, request, **kwargs):
        return render(request, 'account/verification-step-one.html', {'countries': countries})

    @action(detail=False, methods=['GET'], url_path="account/verification/step-two")
    @login_required
    def account_verification_step_two(self, request, **kwargs):
        if not request.user.business.tier0 == models.VERIFIED and not request.user.business.tier1 == models.VERIFIED:
            return self.account_verification_step_one(request, **kwargs)
        return render(request, 'account/verification-step-two.html')

    @action(detail=False, methods=['GET'], url_path="account/verification/step-three")
    @login_required
    def account_verification_step_three(self, request, **kwargs):
        if not request.user.business.tier1 == models.VERIFIED and not request.user.business.tier2 == models.VERIFIED:
            return self.account_verification_step_two(request, **kwargs)
        return render(request, 'account/verification-step-three.html')

    @action(detail=False, methods=['GET'], url_path="account/settlement")
    @login_required
    def account_settlement(self, request, **kwargs):
        active = request.user.mobilemoneysettlementverified.count() + request.user.cryptosettlementverified.count() + request.user.banksettlementverified.count()
        inactive = request.user.mobilemoneysettlementpending.count() + request.user.cryptosettlementpending.count() + request.user.banksettlementpending.count() + request.user.mobilemoneysettlementreview.count() + request.user.cryptosettlementreview.count() + request.user.banksettlementreview.count() + request.user.mobilemoneysettlementunverified.count() + request.user.cryptosettlementunverified.count() + request.user.banksettlementunverified.count()
        return render(request, 'account/settlement.html', {'inactive': inactive, 'active': active})

    @action(detail=False, methods=['GET'], url_path="account/settlement/add")
    @login_required
    def account_settlement_add(self, request, **kwargs):
        return render(request, 'account/settlement-add.html', {'countries': countries})

    @action(detail=False, methods=['GET'], url_path="account/settlement/process/(?P<activation_token>[0-9A-Za-z_\-:]+)")
    @login_required
    def account_process_settlement(self, request, activation_token, **kwargs):
        active = request.user.mobilemoneysettlementverified.count() + request.user.cryptosettlementverified.count() + request.user.banksettlementverified.count()
        inactive = request.user.mobilemoneysettlementpending.count() + request.user.cryptosettlementpending.count() + request.user.banksettlementpending.count() + request.user.mobilemoneysettlementreview.count() + request.user.cryptosettlementreview.count() + request.user.banksettlementreview.count() + request.user.mobilemoneysettlementunverified.count() + request.user.cryptosettlementunverified.count() + request.user.banksettlementunverified.count()
        return render(request, 'account/process-settlement.html', {'activation_token': activation_token, 'inactive': inactive, 'active': active })

    @list_route(methods=["GET"])
    @login_required
    def account(self, request, **kwargs):
        return render(request, 'account/index.html', {'default_device': default_device(request.user) })

    @action(detail=False, methods=['GET'], url_path="account/settings")
    @login_required
    def account_settings(self, request, **kwargs):
        return render(request, 'account/settings.html')

    @action(detail=False, methods=['GET'], url_path="account/details/step-one")
    @login_required
    def account_details_step_one(self, request, **kwargs):
        return render(request, 'account/details-step-one.html', {'countries': countries})

    @action(detail=False, methods=['GET'], url_path="activate-account/(?P<activation_token>[0-9A-Za-z_\-:]+)")
    @login_required
    def activate_account(self, request, activation_token, **kwargs):
        max_age_activate_account = getattr(settings.MAX_AGE_ACTIVATE_ACCOUNT, "MAX_AGE_ACTIVATE_ACCOUNT", None)
        user = get_user_for_token(activation_token, "activate_account",
                                    max_age=max_age_activate_account)
        if request.user == user:
            exc.IntegrityError(_("Failed to activate your account."))
        user.is_email_verified = True
        user.is_active = True
        user.save()
        messages.add_message(request, messages.SUCCESS, _('Thanks for activating your account!'))
        return redirect(reverse('pesaify-dashboard'))

    @action(detail=False, methods=['GET'], url_path="account/cancel/(?P<cancel_token>[0-9A-Za-z_\-:]+)")
    @login_required
    def cancel_account(self, request, cancel_token, **kwargs):
        return render(request, 'account/cancel.html', { "cancel_token": cancel_token })

    @action(detail=False, methods=['GET'], url_path="payments")
    @login_required
    def payments(self, request, **kwargs):
        if self.checks(request, **kwargs):
            invoices = Invoice.objects.filter(owner=request.user)

            if request.GET.get("uuid"):
                invoices = invoices.filter(uuid=request.GET.get("uuid"))

            if request.GET.get("status"):
                invoices = invoices.filter(extra__values__contains=request.GET.get("status").split(","))

            if request.GET.get("startDate") or request.GET.get("endDate"):
                # try:
                start_date = datetime.strptime(request.GET.get("startDate", datetime.now().strftime("%Y-%m-%d")), '%Y-%m-%d').date()
                end_date = datetime.strptime(request.GET.get("endDate", datetime.now().strftime("%Y-%m-%d")), '%Y-%m-%d').date()
                print(start_date)
                print(end_date)
                invoices.filter(current_time__range=(start_date, end_date))
                # except:
                #     pass

            paginator = Paginator(invoices, 5)
            page = request.GET.get('page')

            try:
                invoices = paginator.page(page)
            except PageNotAnInteger:
                invoices = paginator.page(1)
            except EmptyPage:
                invoices = paginator.page(paginator.num_pages)

            for invoice in invoices:
                invoice.get_invoice_update()

            return render(request, 'payment/index.html', {"invoices": invoices})
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="payments/settlements")
    @login_required
    def payments_settlements(self, request, **kwargs):
        if self.checks(request, **kwargs):
            return render(request, 'payment/settlements.html')
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="payment/tools")
    @login_required
    def payment_tools(self, request, **kwargs):
        if self.checks(request, **kwargs):
            return render(request, 'payment/tools/index.html')
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="payment/tools/email")
    @login_required
    def payment_tools_email(self, request, **kwargs):
        if self.checks(request, **kwargs):
            paginator = Paginator(request.user.emailbills, 5)
            page = request.GET.get('page')
            try:
                emailbills = paginator.page(page)
            except PageNotAnInteger:
                emailbills = paginator.page(1)
            except EmptyPage:
                emailbills = paginator.page(paginator.num_pages)

            return render(request, 'payment/tools/email.html', {'emailbills':emailbills})
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="payment/tools/email/add")
    @login_required
    def payment_tools_email_add(self, request, **kwargs):
        if self.checks(request, **kwargs):
            return render(request, 'payment/tools/email-add.html', {'countries': countries, 'currencies': CURRENCY})
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="payment/tools/email/(?P<uuid>[0-9A-Za-z_\-:]+)")
    @login_required
    def payment_tools_email_details(self, request, uuid,**kwargs):
        if self.checks(request, **kwargs):
            bill = get_object_or_404(EmailBill, uuid=uuid, owner=request.user)
            return render(request, 'payment/tools/email-details.html', {'bill': bill, 'countries': countries, 'currencies': CURRENCY})
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="payment/tools/email/duplicate/(?P<uuid>[0-9A-Za-z_\-:]+)")
    @login_required
    def payment_tools_email_duplicate(self, request, uuid,**kwargs):
        if self.checks(request, **kwargs):
            bill = get_object_or_404(EmailBill, uuid=uuid, owner=request.user)
            return render(request, 'payment/tools/email-duplicate.html', {'bill': bill, 'countries': countries, 'currencies': CURRENCY})
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="payment/tools/button")
    @login_required
    def payment_tools_button(self, request, **kwargs):
        if self.checks(request, **kwargs):
            return render(request, 'payment/tools/button.html', {'currencies': CURRENCY})
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="payment/tools/point-of-sale")
    @login_required
    def payment_tools_point_of_sale(self, request, **kwargs):
        if self.checks(request, **kwargs):
            image = get_qrcode(services.get_token_for_user(request.user, "authentication"))
            return render(request, 'payment/tools/point-of-sale.html',{'image': image})
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="payment/tools/web-checkout")
    @login_required
    def payment_tools_web_checkout(self, request, **kwargs):
        if self.checks(request, **kwargs):
            return render(request, 'payment/tools/web-checkout.html', {'currencies': CURRENCY})
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="payment/tools/api-token")
    @login_required
    def payment_tools_api_token(self, request, **kwargs):
        if self.checks(request, **kwargs):
            return render(request, 'payment/tools/api-token.html')
        else:
            return self.dashboard_get_started(request, **kwargs)

    @action(detail=False, methods=['GET'], url_path="i/(?P<uuid>[0-9A-Za-z_\-:]+)")
    def invoice(self, request, uuid,**kwargs):
        invoice = get_object_or_404(Invoice, uuid=uuid)
        invoice.get_invoice_update()
        return render(request, 'payment/invoice-details.html', {'invoice': invoice})

    @action(detail=False, methods=['GET', 'POST'], url_path="invoice/checkout/(?P<uuid>[0-9A-Za-z_\-:]+)")
    @login_required
    def invoice_checkout(self, request, uuid,**kwargs):
        checkout = get_object_or_404(Checkout, uuid=uuid)
        if request.method == "POST":
            if request.data.get('amount'):
                client = PesaifyClient(
                    host=settings.BITCOIN_URL,
                    pem=settings.PRIVKEY,
                    tokens={'merchant': settings.MERCHANT}
                )
                invoice = client.create_invoice({
                    "price": request.data.get('amount'),
                    "currency": checkout.currency,
                    "orderId": request.data.get('order'),
                    "redirectURL": request.user.business.website,
                    "notificationUrl": str(resolve("invoice-notify")),
                    "notificationEmail": checkout.email,
                })
                ct = ContentType.objects.get_for_model(checkout)
                Invoice.objects.create(
                    object_id=checkout.id,
                    content_object=checkout,
                    content_type=ct,
                    uuid=invoice['id'],
                    owner=checkout.owner,
                    creator=request.data.get('employee'),
                    tip=request.data.get('tip'),
                    refund = request.user.business.refund,
                    invoice_time = datetime.utcfromtimestamp(int(str(invoice['invoiceTime'])[:-3])),
                    expiration_time = datetime.utcfromtimestamp(int(str(invoice['expirationTime'])[:-3])),
                    current_time = datetime.utcfromtimestamp(int(str(invoice['currentTime'])[:-3])),
                    extra = invoice,
                    redirect_url = request.user.business.website,
                    notification_url = checkout.ipn,
                    notification_email = checkout.email,
                )
                return redirect(invoice['url'])
            else:
                messages.add_message(request, messages.SUCCESS, _('Please note the amount is required'))
        return render(request, 'iframe/bill/checkout-details.html', {'checkout': checkout})

    @action(detail=False, methods=['GET', 'POST'], url_path="invoice/email/(?P<uuid>[0-9A-Za-z_\-:]+)")
    def invoice_email(self, request, uuid,**kwargs):
        bill = get_object_or_404(EmailBill, uuid=uuid)
        if request.method == "POST":
            client = PesaifyClient(
                host=settings.BITCOIN_URL,
                pem=settings.PRIVKEY,
                tokens={'merchant': settings.MERCHANT}
            )
            invoice = client.create_invoice({"price": bill.amount, "currency": bill.currency})
            invoice = client.create_invoice({
                "price": bill.amount,
                "currency": bill.currency,
                "notificationEmail": bill.owner.email,
                "notificationUrl": str(resolve("invoice-notify")),
            })
            ct = ContentType.objects.get_for_model(bill)
            i = Invoice.objects.create(
                object_id=bill.id,
                content_object=bill,
                content_type=ct,
                uuid=invoice['id'],
                owner=bill.owner,
                refund = bill.owner.business.refund,
                invoice_time = datetime.utcfromtimestamp(int(str(invoice['invoiceTime'])[:-3])),
                expiration_time = datetime.utcfromtimestamp(int(str(invoice['expirationTime'])[:-3])),
                current_time = datetime.utcfromtimestamp(int(str(invoice['currentTime'])[:-3])),
                extra = invoice,
                notification_email = bill.owner.email,
            )
            Buyer.objects.create(
                invoice = i,
                name = request.data.get("name", None),
                address1 = request.data.get("address1", None),
                address2 = request.data.get("address2", None),
                locality = request.data.get("locality", None),
                region = request.data.get("region", None),
                post_code = request.data.get("post_code", None),
                country = request.data.get("country", None),
                phone = request.data.get("phone", None),
            )
            return redirect(invoice['url'])
        return render(request, 'iframe/bill/email-details.html', {'bill': bill, 'countries': countries})

    @action(detail=False, methods=['GET', 'POST'], url_path="invoice/button/(?P<uuid>[0-9A-Za-z_\-:]+)")
    def invoice_button(self, request, uuid,**kwargs):
        button = get_object_or_404(Button, uuid=uuid)
        if request.method == "POST":
            if request.data.get('amount'):
                client = PesaifyClient(
                    host=settings.BITCOIN_URL,
                    pem=settings.PRIVKEY,
                    tokens={'merchant': settings.MERCHANT}
                )
                invoice = client.create_invoice({
                            "price": request.data.get('amount'),
                            "currency": request.data.get('currency', button.currency),
                            "notificationUrl": str(resolve("invoice-notify")),
                            "notificationEmail": button.email,
                            "redirectURL": button.redirect,
                })
                ct = ContentType.objects.get_for_model(button)
                Invoice.objects.create(
                    object_id=button.id,
                    content_object=button,
                    content_type=ct,
                    uuid=invoice['id'],
                    owner=button.owner,
                    creator=request.data.get('donar'),
                    refund = button.owner.business.refund,
                    invoice_time = datetime.utcfromtimestamp(int(str(invoice['invoiceTime'])[:-3])),
                    expiration_time = datetime.utcfromtimestamp(int(str(invoice['expirationTime'])[:-3])),
                    current_time = datetime.utcfromtimestamp(int(str(invoice['currentTime'])[:-3])),
                    extra = invoice,
                    redirect_url = request.user.business.website,
                    notification_url = button.ipn,
                    notification_email = button.email,
                )
                return redirect(invoice['url'])
            else:
                messages.add_message(request, messages.SUCCESS, _('Please note the amount is required'))
        return render(request, 'iframe/bill/button-details.html', {'button': button})



