from django.shortcuts import render
from core.models import *

def index(request):
    index_site_title = GeneralSetting.objects.get(name='index_site_title').parameter
    site_keywords = GeneralSetting.objects.get(name='site_keywords').parameter
    site_description = GeneralSetting.objects.get(name='site_description').parameter
    hero_title = GeneralSetting.objects.get(name='hero_title').parameter
    hero_description = GeneralSetting.objects.get(name='hero_description').parameter
    get_started_btn_link = GeneralSetting.objects.get(name='get_started_btn').description
    get_started_btn_text = GeneralSetting.objects.get(name='get_started_btn').parameter
    watch_video_btn_link =GeneralSetting.objects.get(name='watch_video_btn').description
    watch_video_btn_text = GeneralSetting.objects.get(name='watch_video_btn').parameter

    context = {
        'index_site_title': index_site_title,
        'site_keywords': site_keywords,
        'site_description': site_description,
        'hero_title': hero_title,
        'hero_description': hero_description,
        'get_started_btn_link': get_started_btn_link,
        'get_started_btn_text': get_started_btn_text,
        'watch_video_btn_link': watch_video_btn_link,
        'watch_video_btn_text': watch_video_btn_text,
    }
    return render(request, 'index.html', context=context)

