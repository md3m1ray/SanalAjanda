from django.shortcuts import render
from django.http import JsonResponse

def contact_form(request):
    context = {
        'success': True,
        'message': 'Mesajiniz Iletildi En Kisa Surede Donus Yapilacaktir'
    }
    return JsonResponse(context)