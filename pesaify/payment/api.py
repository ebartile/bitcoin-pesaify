# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from datetime import datetime
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from pesaify.base import exceptions as exc
from pesaify.base import response
from pesaify.base.mails import mail_builder
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_pandas import PandasView
from rest_pandas.renderers import PandasExcelRenderer, PandasCSVRenderer, PandasOldExcelRenderer, PandasJSONRenderer, PandasTextRenderer
from . import serializers
from . import models
from . import permissions

class EmailItemViewSet(ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = (permissions.EmailItemPermission,)
    serializer_class = serializers.EmailItemsSerializer
    queryset = models.EmailItem.objects.all()

    def get_serializer_class(self):
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

    def perform_create(self, serializer):
        obj = serializer.save(owner = self.request.user)
        obj.save()

class EmailBillViewSet(ModelViewSet):
    permission_classes = (permissions.EmailBillPermission,)
    serializer_class = serializers.EmailBillSerializer
    queryset = models.EmailBill.objects.all()

    def get_serializer_class(self):
        if self.action in ["partial_update", "update",]:
            return serializers.EmailBillUpdateSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ["partial_update", "update",]:
            return qs
        return qs.filter(owner=self.request.user)

    def perform_destroy(self, instance):
        objects = models.EmailBillScheduler.objects.filter(bill=instance)
        for obj in objects:
            obj.terminate()

        instance.delete()

    def perform_create(self, serializer):
        obj = serializer.save(owner = self.request.user)
        obj.save()

        for i in range(0, 1000):
            if self.request.data.get('name-items-' + str(i), None) is not None and \
               self.request.data.get('quantity-items-' + str(i), None) is not None and \
               self.request.data.get('price-items-' + str(i), None) is not None:
                models.EmailItem.objects.create(
                    owner=self.request.user,
                    bill = obj,
                    name = self.request.data.get('name-items-' + str(i), None),
                    quantity = self.request.data.get('quantity-items-' + str(i), None),
                    price = self.request.data.get('price-items-' + str(i), None))
            else:
                break

        if obj.recurring:
            models.EmailBillScheduler().schedule_every(obj.owner,obj,'pesaify.payment.tasks.sendemail', self.request.data.get('resend', 'week'), self.request.data.get('send_on', datetime.now()))
        else:
            if obj.delivery == 'email':
                context = {'bill': obj, 'user': self.request.user}

                if serializer.data.get('email', None) is not None:
                    emails = serializer.data.get('email')
                    for x in eval(emails):
                        mail_builder.email_bill(x, context).send()

                if serializer.data.get('cc_email', None) is not None:
                    ccemails = serializer.data.get('cc_email')
                    for x in eval(ccemails):
                        mail_builder.email_bill(x, context).send()

    @detail_route(methods=["GET"])
    def resend(self, request, *args, **kwargs):
        instance = self.get_object()
        emails = instance.email.split(',')
        context = {'bill': instance, 'user': request.user}
        [bool(mail_builder.email_bill(x, context).send()) for x in emails]

        if instance.cc_email:
            ccemails = instance.cc_email.split(',')
            [bool(mail_builder.email_bill(x, context).send()) for x in ccemails]
        return response.NoContent()


class ButtonViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (permissions.ButtonPermission,)
    serializer_class = serializers.ButtonSerializer
    queryset = models.Button.objects.all()

    def get_serializer_class(self):
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

class CheckoutViewSet(ListModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (permissions.CheckoutPermission,)
    serializer_class = serializers.CheckoutSerializer
    queryset = models.Checkout.objects.all()

    def get_serializer_class(self):
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

class InvoiceViewSet(PandasView, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = (permissions.InvoicePermission,)
    serializer_class = serializers.InvoiceSerializer
    queryset = models.Invoice.objects.all()
    renderer_classes = [PandasExcelRenderer, PandasCSVRenderer, PandasOldExcelRenderer, PandasJSONRenderer, PandasTextRenderer]

    def get_serializer_class(self):
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

    @list_route(methods=["POST"])
    def notify(self, request, *args, **kwargs):
        invoice = get_object_or_404(models.Invoice, id=request.data.get("id"))
        invoice.notify = request.data
        invoice.save()
        return response.Ok()

    def get_pandas_filename(self, request, format):
        # Use custom filename and Content-Disposition header
        return "Data Export"  # Extension will be appended automatically
