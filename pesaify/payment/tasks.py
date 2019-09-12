from settings.celery import app
from django.apps import apps as django_apps
from django.utils import timezone
from django.shortcuts import get_object_or_404
from pesaify.base.mails import mail_builder
from .models import EmailBill

@app.task
def sendemail(id):
    obj = get_object_or_404(EmailBill, id=id)
    if obj.delivery == 'email':
        context = {'bill': obj, 'user': obj.owner}

        for x in eval(obj.email):
            mail_builder.email_bill(x, context).send()

        if obj.cc_email is not None:
            for x in eval(obj.ccemails):
                mail_builder.email_bill(x, context).send()

    obj.duplicate()    
