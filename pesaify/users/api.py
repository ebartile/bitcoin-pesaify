# -*- coding: utf-8 -*-
import uuid

from functools import partial
from django.apps import apps
from django.utils.translation import ugettext as _
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from django.contrib.auth import login
from django.db import IntegrityError

from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.serializers import Serializer
from .services import get_user_by_username_or_email
from easy_thumbnails.source_generators import pil_image

from pesaify.base import exceptions as exc
from pesaify.base import response
from pesaify.base.tokens import get_user_for_token, get_settlement_for_token, get_token_for_settlement
from pesaify.base.mails import mail_builder
from pesaify.decorators import check_recaptcha

from . import models
from . import serializers
from . import permissions
from . import services
from .signals import user_cancel_account as user_cancel_account_signal
from .signals import user_change_email as user_change_email_signal
from .throttling import UserDetailRateThrottle, UserUpdateRateThrottle, RegisterFailRateThrottle

def _parse_data(data:dict, *, cls):
    """
    Generic function for parse user data using
    specified validator on `cls` keyword parameter.

    Raises: RequestValidationError exception if
    some errors found when data is validated.

    Returns the parsed data.
    """

    validator = cls(data=data)
    if not validator.is_valid():
        raise exc.RequestValidationError(validator.errors)
    return validator.data

# Parse public register data
parse_public_register_data = partial(_parse_data, cls=serializers.PublicRegisterSerializer)

class UsersViewSet(ModelViewSet):
    permission_classes = (permissions.UserPermission,)
    admin_serializer_class = serializers.UserAdminSerializer
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
    throttle_classes = (UserDetailRateThrottle, UserUpdateRateThrottle)

    def get_throttles(self):
        if self.action in ["create",]:
            self.throttle_classes = [RegisterFailRateThrottle,]
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action in ["partial_update", "update","retrieve",]:
            if self.request.user.is_superuser:
                return self.admin_serializer_class

        if self.action in ["create",]:
            return serializers.PublicRegisterSerializer

        if self.action in ["cancel",]:
            return serializers.CancelAccountValidator

        if self.action in ["change_avatar",]:
            return serializers.ChangeAvatarSerializer

        if self.action in ["change_passport",]:
            return serializers.ChangePassportSerializer

        if self.action in ["change_permit_id_front",]:
            return serializers.ChangePermitIdFrontSerializer

        if self.action in ["change_permit_id_back",]:
            return serializers.ChangePermitIdBackSerializer

        if self.action in ["change_email",]:
            return serializers.ChangeEmailValidator

        if self.action in ["change_password",]:
            return serializers.ChangePasswordSerializer

        if self.action in ["change_password_from_recovery",]:
            return serializers.RecoveryValidator

        if self.action in ["password_recovery",]:
            return serializers.PasswordRecoverySerializer

        if self.action in ["remove_avatar","remove_passport",
                           "remove_permit_id_front", "remove_permit_id_back",
                           "remove_avatar_recording","remove_passport_recording",
                           "remove_permit_id_front_recording", "remove_permit_id_back_recording",
                           "generate_token",]:
            return Serializer

        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(username=self.request.user.username)

    @check_recaptcha
    def create(self, request, *args, **kwargs):
        if not request.recaptcha_is_valid:
            raise exc.BadRequest(_("Invalid Recaptcha"))

        if not settings.PUBLIC_REGISTER_ENABLED:
            raise exc.BadRequest(_("Public register is disabled."))

        try:
            data = parse_public_register_data(request.data)
            data.pop("confirm_password")
            user = services.public_register(**data)
            login(request, user)
        except exc.IntegrityError as e:
            raise exc.BadRequest(e.detail)

        serializer = serializers.UserAdminSerializer(user)
        data = dict(serializer.data)
        data["auth_token"] = services.get_token_for_user(user, "authentication")
        return response.Created(data)

    def partial_update(self, request, *args, **kwargs):
        """
        We must detect if the user is trying to change his email so we can
        save that value and generate a token that allows him to validate it in
        the new email account
        """
        user = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_email = serializer.validated_data.pop('email', None)
        if new_email is not None and new_email != request.user.email:
            valid_new_email = True
            duplicated_email = models.User.objects.filter(email=new_email).exists()

            try:
                domain_name = new_email.split("@")[1]

                if settings.USER_EMAIL_ALLOWED_DOMAINS and domain_name not in settings.USER_EMAIL_ALLOWED_DOMAINS:
                    raise ValidationError(_("You email domain is not allowed"))

                validate_email(new_email)
            except ValidationError:
                valid_new_email = False

            valid_new_email = valid_new_email and new_email != request.user.email

            if duplicated_email:
                raise exc.WrongArguments(_("Duplicated email"))
            elif not valid_new_email:
                raise exc.WrongArguments(_("Not valid email"))

            # We need to generate a token for the email
            request.user.email_token = str(uuid.uuid4())
            request.user.new_email = new_email
            request.user.is_email_verified = False
            request.user.save(update_fields=["email_token", "new_email", "is_email_verified"])
            email = mail_builder.change_email(
                request.user.new_email,
                {
                    "user": request.user,
                    "lang": request.user.lang
                }
            )
            email.send()

            if not request.data._mutable:
                request.data._mutable = True

            request.data.pop('email')
            return super().partial_update(request, *args, **kwargs)
        else:
            if request.user.is_verified == models.VERIFIED:
                exc.PermissionDenied("Please note that once you have been verified. This information can not change. Please contact <a href='mailto:support@pesaify.com'>support@pesaify.com</a> for help.")

            request.user.is_verified = models.REVIEW
            request.user.save(update_fields=["is_verified"])
            return super().partial_update(request, *args, **kwargs)

    @list_route(methods=["POST"])
    def password_recovery(self, request, pk=None):
        username_or_email = request.data.get('username', None)

        if not username_or_email:
            raise exc.WrongArguments(_("Invalid username or email"))

        user = get_user_by_username_or_email(username_or_email)
        user.token = str(uuid.uuid4())
        user.save(update_fields=["token"])

        email = mail_builder.password_recovery(user, {"user": user})
        email.send()

        return response.Ok({"detail": _("Mail sent successful!")})

    @list_route(methods=["POST"])
    def change_password_from_recovery(self, request, pk=None):
        """
        Change password with token (from password recovery step).
        """
        validator = serializers.RecoveryValidator(data=request.data, many=False)
        if not validator.is_valid():
            raise exc.RequestValidationError(validator.errors)

        try:
            user = models.User.objects.get(token=validator.data["token"])
        except models.User.DoesNotExist:
            raise exc.WrongArguments(_("Token is invalid"))

        user.set_password(validator.data["password"])
        user.token = None
        user.save(update_fields=["password", "token"])

        return response.NoContent()

    @list_route(methods=["POST"])
    def change_password(self, request, pk=None):
        """
        Change password to current logged user.
        """

        validator = serializers.ChangePasswordSerializer(data=request.data, many=False)
        if not validator.is_valid():
            raise exc.RequestValidationError(validator.errors)

        current_password = validator.data["current_password"]
        password = validator.data["password"]

        if current_password and not request.user.check_password(current_password):
            raise exc.WrongArguments(_("Invalid current password"))

        request.user.set_password(password)
        request.user.save(update_fields=["password"])
        return response.NoContent()

    @list_route(methods=["GET"])
    def generate_token(self, request, *args, **kwargs):
        request.user.token = services.get_token_for_user(request.user, "token")
        request.user.save(update_fields=["token",])

        return response.Created({'token': request.user.token})

    @list_route(methods=["GET"])
    def resend_change_email(self, request, *args, **kwargs):
        if request.user.new_email is None:
            request.user.new_email = request.user.email

        request.user.email_token = str(uuid.uuid4())
        request.user.is_email_verified = False
        request.user.save(update_fields=["email_token", "is_email_verified", "new_email",])

        email = mail_builder.change_email(
            request.user.new_email,
            {
                "user": request.user,
                "lang": request.user.lang
            }
        )
        email.send()

        return response.NoContent()

    def destroy(self, request, pk=None):
        user = self.get_object()
        stream = request.stream
        request_data = stream is not None and stream.GET or None
        user_cancel_account_signal.send(sender=user.__class__, user=user, request_data=request_data)
        user.cancel()
        return response.NoContent()

    @list_route(methods=["POST"])
    def change_avatar(self, request):
        """
        Change avatar to current logged user.
        """

        avatar = request.FILES.get('avatar', None)
        avatar_recording = request.FILES.get('avatar_recording', None)

        if not avatar_recording:
            raise exc.WrongArguments(_("Incomplete arguments"))

        if not avatar:
            raise exc.WrongArguments(_("Incomplete arguments"))

        try:
            pil_image(avatar)
        except Exception:
            raise exc.WrongArguments(_("Invalid image format"))


        request.user.photo_recording = avatar_recording
        request.user.photo = avatar
        request.user.save(update_fields=["photo","photo_recording"])
        user_data = self.admin_serializer_class(request.user).data

        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def change_passport(self, request):
        """
        Change passport to current logged user.
        """

        passport = request.FILES.get('passport', None)
        passport_recording = request.FILES.get('passport_recording', None)

        if not passport_recording:
            raise exc.WrongArguments(_("Incomplete arguments"))

        if not passport:
            raise exc.WrongArguments(_("Incomplete arguments"))

        try:
            pil_image(passport)
        except Exception:
            raise exc.WrongArguments(_("Invalid image format"))

        request.user.passport_recording = passport_recording
        request.user.passport = passport
        request.user.save(update_fields=["passport","passport_recording"])
        user_data = self.admin_serializer_class(request.user).data

        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def change_permit_id_front(self, request):
        """
        Change permit or id front to current logged user.
        """

        permit_id_front = request.FILES.get('permit_id_front', None)
        permit_id_front_recording = request.FILES.get('permit_id_front_recording', None)

        if not permit_id_front_recording:
            raise exc.WrongArguments(_("Incomplete arguments"))

        if not permit_id_front:
            raise exc.WrongArguments(_("Incomplete arguments"))

        try:
            pil_image(permit_id_front)
        except Exception:
            raise exc.WrongArguments(_("Invalid image format"))

        request.user.permit_id_front_recording = permit_id_front_recording
        request.user.permit_id_front = permit_id_front
        request.user.save(update_fields=["permit_id_front","permit_id_front_recording"])
        user_data = self.admin_serializer_class(request.user).data

        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def change_permit_id_back(self, request):
        """
        Change permit or id back to current logged user.
        """

        permit_id_back = request.FILES.get('permit_id_back', None)
        permit_id_back_recording = request.FILES.get('permit_id_back_recording', None)

        if not permit_id_back:
            raise exc.WrongArguments(_("Incomplete arguments"))

        if not permit_id_back_recording:
            raise exc.WrongArguments(_("Incomplete arguments"))

        try:
            pil_image(permit_id_back)
        except Exception:
            raise exc.WrongArguments(_("Invalid image format"))

        request.user.permit_id_back_recording = permit_id_back_recording
        request.user.permit_id_back = permit_id_back
        request.user.save(update_fields=["permit_id_back", "permit_id_back_recording"])
        user_data = self.admin_serializer_class(request.user).data

        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def remove_avatar(self, request):
        """
        Remove the avatar of current logged user.
        """
        request.user.photo = None
        request.user.save(update_fields=["photo"])
        user_data = self.admin_serializer_class(request.user).data
        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def remove_passport(self, request):
        """
        Remove the passport of current logged user.
        """
        request.user.passport = None
        request.user.save(update_fields=["passport"])
        user_data = self.admin_serializer_class(request.user).data
        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def remove_permit_id_front(self, request):
        """
        Remove the permit or id front of current logged user.
        """
        request.user.permit_id_front = None
        request.user.save(update_fields=["permit_id_front"])
        user_data = self.admin_serializer_class(request.user).data
        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def remove_permit_id_back(self, request):
        """
        Remove the permit or id back of current logged user.
        """
        request.user.permit_id_back = None
        request.user.save(update_fields=["permit_id_back"])
        user_data = self.admin_serializer_class(request.user).data
        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def remove_avatar_recording(self, request):
        """
        Remove the avatar recording of current logged user.
        """
        request.user.photo_recording = None
        request.user.save(update_fields=["photo_recording"])
        user_data = self.admin_serializer_class(request.user).data
        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def remove_passport_recording(self, request):
        """
        Remove the passport recording of current logged user.
        """
        request.user.passport_recording = None
        request.user.save(update_fields=["passport_recording"])
        user_data = self.admin_serializer_class(request.user).data
        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def remove_permit_id_front_recording(self, request):
        """
        Remove the permit or id front recording of current logged user.
        """
        request.user.permit_id_front_recording = None
        request.user.save(update_fields=["permit_id_front_recording"])
        user_data = self.admin_serializer_class(request.user).data
        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def remove_permit_id_back_recording(self, request):
        """
        Remove the permit or id back recording of current logged user.
        """
        request.user.permit_id_back_recording = None
        request.user.save(update_fields=["permit_id_back_recording"])
        user_data = self.admin_serializer_class(request.user).data
        return response.Ok(user_data)

    @list_route(methods=["POST"])
    def change_email(self, request, pk=None):
        """
        Verify the email change to current logged user.
        """
        validator = serializers.ChangeEmailValidator(data=request.data, many=False)
        if not validator.is_valid():
            raise exc.WrongArguments(_("Invalid, are you sure the token is correct and you "
                                       "didn't use it before?"))

        try:
            user = models.User.objects.get(email_token=validator.data["email_token"])
        except models.User.DoesNotExist:
            raise exc.WrongArguments(_("Invalid, are you sure the token is correct and you "
                                       "didn't use it before?"))

        old_email = user.email
        new_email = user.new_email

        user.username = new_email
        user.email = new_email
        user.new_email = None
        user.email_token = None
        user.is_email_verified = True
        user.save(update_fields=["username","email", "new_email", "email_token", "is_email_verified"])
        user_change_email_signal.send(sender=user.__class__,
                                      user=user,
                                      old_email=old_email,
                                      new_email=new_email)

        return response.NoContent()

    @list_route(methods=["POST"])
    def cancel(self, request, pk=None):
        """
        Cancel an account via token
        """
        validator = serializers.CancelAccountValidator(data=request.data, many=False)
        if not validator.is_valid():
            raise exc.WrongArguments(_("Invalid, are you sure the token is correct?"))

        try:
            max_age_cancel_account = getattr(settings, "MAX_AGE_CANCEL_ACCOUNT", None)
            user = get_user_for_token(validator.data["cancel_token"], "cancel_account",
                                      max_age=max_age_cancel_account)

        except exc.NotAuthenticated:
            raise exc.WrongArguments(_("Invalid, are you sure the token is correct?"))

        user.cancel()
        return response.NoContent()

class BusinessViewSet(UpdateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = (permissions.BusinessPermission,)
    serializer_class = serializers.BusinessSerializer
    queryset = models.Business.objects.all()

    def get_serializer_class(self):
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """
        We must detect if the user is trying to change his email so we can
        save that value and generate a token that allows him to validate it in
        the new email account
        """
        business = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.data.get('notify') or serializer.data.get('speed') or serializer.data.get('refund'):
            pass
        else:
            if request.GET.get('step', None) == "2":
                business.tier1 = models.REVIEW
                business.save()

            elif request.GET.get('step', None) == "3":
                business.tier2 = models.REVIEW
                business.save()

            else:
                business.tier0 = models.REVIEW
                business.save()

        return super().partial_update(request, *args, **kwargs)


class MobileMoneySettlementViewSet(ModelViewSet):
    permission_classes = (permissions.SettlementPermission,)
    serializer_class = serializers.MobileMoneySerializer
    queryset = models.MobileMoneySettlement.objects.all()

    def get_serializer_class(self):
        if self.action in ["activate",]:
            return serializers.ActivateSettlementValidator

        if self.action in ["destroy","resend",]:
            return Serializer

        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user, business=self.request.user.business)

    def perform_create(self, serializer):
        obj = serializer.save(owner = self.request.user, business=self.request.user.business, is_verified=models.PENDING)
        obj.save()
        token = get_token_for_settlement(obj, "activate_settlement")
        obj.token = token
        obj.save()
        context = {"user": self.request.user, "settlement": obj}
        email = mail_builder.change_settlement(self.request.user, context)
        email.send()

    def perform_update(self, serializer):
        token = get_token_for_settlement(serializer.instance, "activate_settlement")
        serializer.instance.token = token
        serializer.instance.is_verified = models.REVIEW
        context = {"user": self.request.user, "settlement": serializer.instance}
        email = mail_builder.change_settlement(self.request.user, context)
        email.send()
        serializer.save()

    @list_route(methods=["POST"])
    def activate(self, request, pk=None):
        """
        Activate settlement an account via token
        """
        validator = serializers.ActivateSettlementValidator(data=request.data, many=False)
        if not validator.is_valid():
            raise exc.WrongArguments(_("Invalid, are you sure the token is correct?"))

        try:
            max_age_activate_account = getattr(settings, "MAX_AGE_ACTIVATE_SETTLEMENT", None)
            settlement_id = get_settlement_for_token(validator.data["activation_token"], "activate_settlement",
                                      max_age=max_age_activate_account)
            settlement = models.MobileMoneySettlement.objects.get(id=settlement_id, owner=request.user)
            settlement.token = None
            settlement.is_verified = models.REVIEW
            settlement.save()
        except exc.NotAuthenticated:
            raise exc.WrongArguments(_("Invalid, are you sure the token is correct?"))

        return response.NoContent()

    @detail_route(methods=["GET"])
    def resend(self, request, *args, **kwargs):
        instance = self.get_object()
        token = get_token_for_settlement(instance, "activate_settlement")
        instance.token = token
        instance.is_verified = models.PENDING
        context = {"user": self.request.user, "settlement": instance}
        email = mail_builder.change_settlement(self.request.user, context)
        email.send()
        instance.save()
        return response.NoContent()


class BankSettlementViewSet(ModelViewSet):
    permission_classes = (permissions.SettlementPermission,)
    serializer_class = serializers.BankSettlementSerializer
    queryset = models.BankSettlement.objects.all()

    def get_serializer_class(self):
        if self.action in ["activate",]:
            return serializers.ActivateSettlementValidator

        if self.action in ["destroy","resend",]:
            return Serializer

        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user, business=self.request.user.business)

    def perform_create(self, serializer):
        obj = serializer.save(owner = self.request.user, business=self.request.user.business, is_verified=models.PENDING)
        obj.save()
        token = get_token_for_settlement(obj, "activate_settlement")
        obj.token = token
        obj.save()
        context = {"user": self.request.user, "settlement": obj}
        email = mail_builder.change_settlement(self.request.user, context)
        email.send()

    def perform_update(self, serializer):
        token = get_token_for_settlement(serializer.instance, "activate_settlement")
        serializer.instance.token = token
        serializer.instance.is_verified = models.REVIEW
        context = {"user": self.request.user, "settlement": serializer.instance}
        email = mail_builder.change_settlement(self.request.user, context)
        email.send()
        serializer.save()

    @list_route(methods=["POST"])
    def activate(self, request, pk=None):
        """
        Activate settlement an account via token
        """
        validator = serializers.ActivateSettlementValidator(data=request.data, many=False)
        if not validator.is_valid():
            raise exc.WrongArguments(_("Invalid, are you sure the token is correct?"))

        try:
            max_age_activate_account = getattr(settings, "MAX_AGE_ACTIVATE_SETTLEMENT", None)
            settlement_id = get_settlement_for_token(validator.data["activation_token"], "activate_settlement",
                                      max_age=max_age_activate_account)
            settlement = models.BankSettlement.objects.get(id=settlement_id, owner=request.user)
            settlement.token = None
            settlement.is_verified = models.REVIEW
            settlement.save()
        except exc.NotAuthenticated:
            raise exc.WrongArguments(_("Invalid, are you sure the token is correct?"))

        return response.NoContent()

    @detail_route(methods=["GET"])
    def resend(self, request, *args, **kwargs):
        instance = self.get_object()
        token = get_token_for_settlement(instance, "activate_settlement")
        instance.token = token
        instance.is_verified = models.PENDING
        context = {"user": self.request.user, "settlement": instance}
        email = mail_builder.change_settlement(self.request.user, context)
        email.send()
        instance.save()
        return response.NoContent()


class CryptoSettlementViewSet(ModelViewSet):
    permission_classes = (permissions.SettlementPermission,)
    serializer_class = serializers.CryptoSettlementSerializer
    queryset = models.CryptoSettlement.objects.all()

    def get_serializer_class(self):
        if self.action in ["activate",]:
            return serializers.ActivateSettlementValidator

        if self.action in ["destroy","resend",]:
            return Serializer

        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user, business=self.request.user.business)

    def perform_create(self, serializer):
        obj = serializer.save(owner = self.request.user, business=self.request.user.business, is_verified=models.PENDING)
        obj.save()
        token = get_token_for_settlement(obj, "activate_settlement")
        obj.token = token
        obj.save()
        context = {"user": self.request.user, "settlement": obj}
        email = mail_builder.change_settlement(self.request.user, context)
        email.send()

    def perform_update(self, serializer):
        token = get_token_for_settlement(serializer.instance, "activate_settlement")
        serializer.instance.token = token
        serializer.instance.is_verified = models.REVIEW
        context = {"user": self.request.user, "settlement": serializer.instance}
        email = mail_builder.change_settlement(self.request.user, context)
        email.send()
        serializer.save()


    @list_route(methods=["POST"])
    def activate(self, request, pk=None):
        """
        Activate settlement an account via token
        """
        validator = serializers.ActivateSettlementValidator(data=request.data, many=False)
        if not validator.is_valid():
            raise exc.WrongArguments(_("Invalid, are you sure the token is correct?"))

        try:
            max_age_activate_account = getattr(settings, "MAX_AGE_ACTIVATE_SETTLEMENT", None)
            settlement_id = get_settlement_for_token(validator.data["activation_token"], "activate_settlement",
                                      max_age=max_age_activate_account)
            settlement = models.CryptoSettlement.objects.get(id=settlement_id, owner=request.user)
            settlement.token = None
            settlement.is_verified = models.REVIEW
            settlement.save()
        except exc.NotAuthenticated:
            raise exc.WrongArguments(_("Invalid, are you sure the token is correct?"))

        return response.NoContent()

    @detail_route(methods=["GET"])
    def resend(self, request, *args, **kwargs):
        instance = self.get_object()
        token = get_token_for_settlement(instance, "activate_settlement")
        instance.token = token
        instance.is_verified = models.PENDING
        context = {"user": self.request.user, "settlement": instance}
        email = mail_builder.change_settlement(self.request.user, context)
        email.send()
        instance.save()
        return response.NoContent()


