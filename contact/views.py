from django.shortcuts import render
from django.http import JsonResponse
from core.models import GeneralSetting


def contact_form(request):
    context = {
        'success': True,
        'message': 'Mesaj Iletildi'
    }
    return JsonResponse(context)

def contact(request):
    settings = {setting.name: setting for setting in GeneralSetting.objects.all()}

    def get_setting_parameter(name, default=None):
        return settings.get(name).parameter if name in settings else default

    def get_setting_description(name, default=None):
        return settings.get(name).description if name in settings else default

    context = {
        'contact_site_title': get_setting_parameter('contact_site_title', 'Sanal Ajanda İletişim'),

    }
    return render(request, 'contact.html', context=context)