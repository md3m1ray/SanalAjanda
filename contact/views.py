from django.contrib.messages import success
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import JsonResponse
from pyexpat.errors import messages
from core.models import GeneralSetting
from contact.models import Contact
from contact.forms import ContactForm


def contact_form(request):
    if request.POST:

        contact_form = ContactForm(request.POST or None)

        if contact_form.is_valid():
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            contact_form.send_mail()

            success = True
            message = 'Form submitted successfully'
        else:
            success = False
            message = 'Valid Error'
    else:
        success = False
        message = 'Valid Error'

    context = {
        'success': success,
        'message': message
    }
    return JsonResponse(context)


def contact(request):
    contact_form = ContactForm()

    settings = {setting.name: setting for setting in GeneralSetting.objects.all()}

    def get_setting_parameter(name, default=None):
        return settings.get(name).parameter if name in settings else default

    context = {
        'contact_site_title': get_setting_parameter('contact_site_title',
                                                    'Sanal Ajanda İletişim'),
        'contact_form': contact_form,

    }
    return render(request, 'contact.html', context=context)
