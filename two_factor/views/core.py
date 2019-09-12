import logging
import warnings
from base64 import b32encode
from binascii import unhexlify

import django_otp
import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.sites.shortcuts import get_current_site
from django.forms import Form
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.http import is_safe_url
from django.utils.module_loading import import_string
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import DeleteView, FormView, TemplateView
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required
from django_otp.decorators import otp_required
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.util import random_hex
from django import forms

from two_factor import signals
from two_factor.models import get_available_methods
from two_factor.utils import totp_digits
from pesaify.decorators import login_forbidden_class, login_required_class

from ..forms import (
    AuthenticationTokenForm, BackupTokenForm, DeviceValidationForm, MethodForm, TOTPDeviceForm
)
from ..utils import default_device, get_otpauth_url
from .utils import IdempotentSessionWizardView, class_view_decorator
from django import forms
from pesaify.users.services import get_and_validate_user


logger = logging.getLogger(__name__)


class AuthForm(AuthenticationForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True,'class': 'form-control'}), label=_("Email"))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:

            try:
                self.user_cache =  get_and_validate_user(username=username, password=password)
            except Exception:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )

            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

@class_view_decorator(login_forbidden_class)
@class_view_decorator(sensitive_post_parameters())
@class_view_decorator(never_cache)
class LoginView(IdempotentSessionWizardView):
    """
    View for handling the login process, including OTP verification.

    The login process is composed like a wizard. The first step asks for the
    user's credentials. If the credentials are correct, the wizard proceeds to
    the OTP verification step. If the user has a default OTP device configured,
    that device is asked to generate a token and the
    user is asked to provide the generated token. The backup devices are also
    listed, allowing the user to select a backup device for verification.
    """
    template_name = 'two_factor/core/login.html'
    form_list = (
        ('auth', AuthForm),
        ('token', AuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )
    idempotent_dict = {
        'token': False,
        'backup': False,
    }

    def has_token_step(self):
        return default_device(self.get_user())

    def has_backup_step(self):
        return default_device(self.get_user()) and \
            'token' not in self.storage.validated_step_data

    condition_dict = {
        'token': has_token_step,
        'backup': has_backup_step,
    }
    redirect_field_name = REDIRECT_FIELD_NAME

    def __init__(self, **kwargs):
        super(LoginView, self).__init__(**kwargs)
        self.user_cache = None
        self.device_cache = None

    def post(self, *args, **kwargs):
        """
        The user can select a particular device to challenge, being the backup
        devices added to the account.
        """

        return super(LoginView, self).post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        """
        Login the user and redirect to the desired page.
        """
        login(self.request, self.get_user())

        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )

        if not is_safe_url(url=redirect_to, allowed_hosts=[self.request.get_host()]):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        device = getattr(self.get_user(), 'otp_device', None)
        if device:
            signals.user_verified.send(sender=__name__, request=self.request,
                                       user=self.get_user(), device=device)
        return redirect(redirect_to)

    def get_form_kwargs(self, step=None):
        """
        AuthenticationTokenForm requires the user kwarg.
        """
        if step == 'auth':
            return {
                'request': self.request
            }
        if step in ('token', 'backup'):
            return {
                'user': self.get_user(),
                'initial_device': self.get_device(step),
            }
        return {}

    def get_device(self, step=None):
        """
        Returns the OTP device selected by the user, or his default device.
        """
        if not self.device_cache:
            if step == 'backup':
                try:
                    self.device_cache = self.get_user().staticdevice_set.get(name='backup')
                except StaticDevice.DoesNotExist:
                    pass
            if not self.device_cache:
                self.device_cache = default_device(self.get_user())
        return self.device_cache

    def render(self, form=None, **kwargs):
        """
        If the user selected a device, ask the device to generate a challenge;
        sending a text message.
        """
        if self.steps.current == 'token':
            self.get_device().generate_challenge()
        return super(LoginView, self).render(form, **kwargs)

    def get_user(self):
        """
        Returns the user authenticated by the AuthenticationForm. Returns False
        if not a valid user; see also issue #65.
        """
        if not self.user_cache:
            form_obj = self.get_form(step='auth',
                                     data=self.storage.get_step_data('auth'))
            self.user_cache = form_obj.is_valid() and form_obj.user_cache
        return self.user_cache

    def get_context_data(self, form, **kwargs):
        """
        Adds user's default and backup OTP devices to the context.
        """
        context = super(LoginView, self).get_context_data(form, **kwargs)
        if self.steps.current == 'token':
            context['device'] = self.get_device()
            try:
                context['backup_tokens'] = self.get_user().staticdevice_set\
                    .get(name='backup').token_set.count()
            except StaticDevice.DoesNotExist:
                context['backup_tokens'] = 0

        if getattr(settings, 'LOGOUT_REDIRECT_URL', None):
            context['cancel_url'] = resolve_url(settings.LOGOUT_REDIRECT_URL)
        elif getattr(settings, 'LOGOUT_URL', None):
            warnings.warn(
                "LOGOUT_URL has been replaced by LOGOUT_REDIRECT_URL, please "
                "review the URL and update your settings.",
                DeprecationWarning)
            context['cancel_url'] = resolve_url(settings.LOGOUT_URL)
        return context


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class SetupView(IdempotentSessionWizardView):
    """
    View for handling OTP setup using a wizard.

    The first step of the wizard shows an introduction text, explaining how OTP
    works and why it should be enabled. The user has to select the verification
    method (generator / sms) in the second step. Depending on the method
    selected, the third step configures the device. For the generator method, a
    QR code is shown which can be scanned using a mobile phone app and the user
    is asked to provide a generated token. For sms methods, the user
    provides the phone number which is then validated in the final step.
    """
    success_url = 'two_factor:setup_complete'
    qrcode_url = 'two_factor:qr'
    template_name = 'two_factor/core/setup.html'
    session_key_name = 'django_two_factor-qr_secret_key'
    initial_dict = {}
    form_list = (
        ('welcome', Form),
        ('method', MethodForm),
        ('generator', TOTPDeviceForm),
        ('validation', DeviceValidationForm),
    )
    condition_dict = {
        'generator': lambda self: self.get_method() == 'generator',
        'validation': lambda self: self.get_method() in (),
    }
    idempotent_dict = {
    }

    def get_method(self):
        method_data = self.storage.validated_step_data.get('method', {})
        return method_data.get('method', None)

    def get(self, request, *args, **kwargs):
        """
        Start the setup wizard. Redirect if already enabled.
        """
        if default_device(self.request.user):
            return redirect(self.success_url)
        return super(SetupView, self).get(request, *args, **kwargs)

    def get_form_list(self):
        """
        Check if there is only one method, then skip the MethodForm from form_list
        """
        form_list = super(SetupView, self).get_form_list()
        available_methods = get_available_methods()
        if len(available_methods) == 1:
            form_list.pop('method', None)
            method_key, _ = available_methods[0]
            self.storage.validated_step_data['method'] = {'method': method_key}
        return form_list

    def render_next_step(self, form, **kwargs):
        """
        In the validation step, ask the device to generate a challenge.
        """
        next_step = self.steps.next
        if next_step == 'validation':
            try:
                self.get_device().generate_challenge()
                kwargs["challenge_succeeded"] = True
            except Exception:
                logger.exception("Could not generate challenge")
                kwargs["challenge_succeeded"] = False
        return super(SetupView, self).render_next_step(form, **kwargs)

    def done(self, form_list, **kwargs):
        """
        Finish the wizard. Save all forms and redirect.
        """
        # Remove secret key used for QR code generation
        try:
            del self.request.session[self.session_key_name]
        except KeyError:
            pass

        # TOTPDeviceForm
        if self.get_method() == 'generator':
            form = [form for form in form_list if isinstance(form, TOTPDeviceForm)][0]
            device = form.save()
        else:
            raise NotImplementedError("Unknown method '%s'" % self.get_method())

        django_otp.login(self.request, device)
        return redirect(self.success_url)

    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == 'generator':
            kwargs.update({
                'key': self.get_key(step),
                'user': self.request.user,
            })
        metadata = self.get_form_metadata(step)
        if metadata:
            kwargs.update({
                'metadata': metadata,
            })
        return kwargs

    def get_device(self, **kwargs):
        """
        Uses the data from the setup step and generated key to recreate device.

        Only used for sms -- generator uses other procedure.
        """
        method = self.get_method()
        kwargs = kwargs or {}
        kwargs['name'] = 'default'
        kwargs['user'] = self.request.user

    def get_key(self, step):
        self.storage.extra_data.setdefault('keys', {})
        if step in self.storage.extra_data['keys']:
            return self.storage.extra_data['keys'].get(step)
        key = random_hex(20).decode('ascii')
        self.storage.extra_data['keys'][step] = key
        return key

    def get_context_data(self, form, **kwargs):
        context = super(SetupView, self).get_context_data(form, **kwargs)
        if self.steps.current == 'generator':
            key = self.get_key('generator')
            rawkey = unhexlify(key.encode('ascii'))
            b32key = b32encode(rawkey).decode('utf-8')
            self.request.session[self.session_key_name] = b32key
            context.update({
                'QR_URL': reverse(self.qrcode_url)
            })
        elif self.steps.current == 'validation':
            device = self.get_device()
            context['device'] = device
        context['cancel_url'] = resolve_url('two_factor:profile')
        return context

    def process_step(self, form):
        if hasattr(form, 'metadata'):
            self.storage.extra_data.setdefault('forms', {})
            self.storage.extra_data['forms'][self.steps.current] = form.metadata
        return super(SetupView, self).process_step(form)

    def get_form_metadata(self, step):
        self.storage.extra_data.setdefault('forms', {})
        return self.storage.extra_data['forms'].get(step, None)


@class_view_decorator(never_cache)
@class_view_decorator(otp_required)
class BackupTokensView(FormView):
    """
    View for listing and generating backup tokens.

    A user can generate a number of static backup tokens. When the user loses
    its phone, these backup tokens can be used for verification. These backup
    tokens should be stored in a safe location; either in a safe or underneath
    a pillow ;-).
    """
    form_class = Form
    success_url = 'two_factor:backup_tokens'
    template_name = 'two_factor/core/backup_tokens.html'
    number_of_tokens = 10

    def get_device(self):
        return self.request.user.staticdevice_set.get_or_create(name='backup')[0]

    def get_context_data(self, **kwargs):
        context = super(BackupTokensView, self).get_context_data(**kwargs)
        context['device'] = self.get_device()
        return context

    def form_valid(self, form):
        """
        Delete existing backup codes and generate new ones.
        """
        device = self.get_device()
        device.token_set.all().delete()
        for n in range(self.number_of_tokens):
            device.token_set.create(token=StaticToken.random_token())

        return redirect(self.success_url)


@class_view_decorator(never_cache)
@class_view_decorator(otp_required)
class SetupCompleteView(TemplateView):
    """
    View congratulation the user when OTP setup has completed.
    """
    template_name = 'two_factor/core/setup_complete.html'

    def get_context_data(self):
        return {
        }


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class QRGeneratorView(View):
    """
    View returns an SVG image with the OTP token information
    """
    http_method_names = ['get']
    default_qr_factory = 'qrcode.image.svg.SvgPathImage'
    session_key_name = 'django_two_factor-qr_secret_key'

    # The qrcode library only supports PNG and SVG for now
    image_content_types = {
        'PNG': 'image/png',
        'SVG': 'image/svg+xml; charset=utf-8',
    }

    def get(self, request, *args, **kwargs):
        # Get the data from the session
        try:
            key = self.request.session[self.session_key_name]
        except KeyError:
            raise Http404()

        # Get data for qrcode
        image_factory_string = getattr(settings, 'TWO_FACTOR_QR_FACTORY', self.default_qr_factory)
        image_factory = import_string(image_factory_string)
        content_type = self.image_content_types[image_factory.kind]
        try:
            username = self.request.user.get_username()
        except AttributeError:
            username = self.request.user.username

        otpauth_url = get_otpauth_url(accountname=username,
                                      issuer=get_current_site(self.request).name,
                                      secret=key,
                                      digits=totp_digits())

        # Make and return QR code
        img = qrcode.make(otpauth_url, image_factory=image_factory)
        resp = HttpResponse(content_type=content_type)
        img.save(resp)
        return resp
