from django.shortcuts import render
from core.models import GeneralSetting


def index(request):
    settings = {setting.name: setting for setting in GeneralSetting.objects.all()}

    def get_setting_parameter(name, default=None):
        return settings.get(name).parameter if name in settings else default

    def get_setting_description(name, default=None):
        return settings.get(name).description if name in settings else default

    context = {
        'index_site_title': get_setting_parameter('index_site_title', 'Sanal Ajanda'),
        'site_keywords': get_setting_parameter('site_keywords',
                                               'sanalajanda,ajanda,takvim,sanalajandatakvim,planlaici,planlaici takvim,planlaici takvimi'),
        'site_description': get_setting_parameter('site_description', 'Sanal Ajanda'),
        'hero_title': get_setting_parameter('hero_title', 'Sanal Ajanda'),
        'hero_description': get_setting_parameter('hero_description', 'Sanal Ajanda'),
        'get_started_btn_link': get_setting_description('get_started_btn', '#'),
        'get_started_btn_text': get_setting_parameter('get_started_btn', 'Hemen Başlayın'),
        'watch_video_btn_link': get_setting_description('watch_video_btn', '#'),
        'watch_video_btn_text': get_setting_parameter('watch_video_btn', 'Videoyu İzle'),
        'stats_member_num': get_setting_parameter('stats_member', '175'),
        'stats_member_text': get_setting_description('stats_member', 'Mutlu Üye'),
        'stats_days_num': get_setting_parameter('stats_days', '1350'),
        'stats_days_text': get_setting_description('stats_days', 'Planlı Gün'),
        'stats_notes_num': get_setting_parameter('stats_notes', '1580'),
        'stats_notes_text': get_setting_description('stats_notes', 'Etkinlik / Not'),
        'stats_other_num': get_setting_parameter('stats_other', '3'),
        'stats_other_text': get_setting_description('stats_other', 'Ekip Arkadaşı'),
        'service_1_title' : get_setting_parameter('service_1_title', 'Takvim'),
        'service_1_text' : get_setting_parameter('service_1_text', 'Takvim'),
        'service_2_title': get_setting_parameter('service_2_title', 'Takvim'),
        'service_2_text': get_setting_parameter('service_2_text', 'Takvim'),
        'service_3_title': get_setting_parameter('service_3_title', 'Takvim'),
        'service_3_text': get_setting_parameter('service_3_text', 'Takvim'),
        'service_4_title': get_setting_parameter('service_4_title', 'Takvim'),
        'service_4_text': get_setting_parameter('service_4_text', 'Takvim'),
        'service_5_title': get_setting_parameter('service_5_title', 'Takvim'),
        'service_5_text': get_setting_parameter('service_5_text', 'Takvim'),
        'service_6_title': get_setting_parameter('service_6_title', 'Takvim'),
        'service_6_text': get_setting_parameter('service_6_text', 'Takvim'),
    }

    return render(request, 'index.html', context=context)
