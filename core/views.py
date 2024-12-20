from django.shortcuts import render
from core.models import GeneralSetting, FooterSetting, PricingSetting, FaqSetting, ImgUpload, NavbarSetting


def get_settings(model, name_field='name'):
    return {getattr(item, name_field): item for item in model.objects.all()}


def load_settings():
    return {
        'general_settings': get_settings(GeneralSetting),
        'footer_settings': get_settings(FooterSetting),
        'pricing_settings': get_settings(PricingSetting),
        'faq_settings': get_settings(FaqSetting),
        'uploaded_images': ImgUpload.objects.all(),
    }


def base(request):
    context = load_settings()

    general_settings = context['general_settings']

    context['navbar_items'] = get_navbar_settings()

    context.update({
        'index_site_title': general_settings.get('index_site_title', 'Sanal Ajanda').parameter,
        'site_keywords': general_settings.get('site_keywords', 'sanalajanda,ajanda,takvim').parameter,
        'site_description': general_settings.get('site_description', 'Sanal Ajanda').parameter,
    })

    return context


def index(request):
    context = load_settings()

    pricing_context = get_pricing_settings()
    context.update(pricing_context)

    context['faq_list'] = get_faq_settings()

    general_settings = context['general_settings']

    context.update({
        'hero_title': general_settings.get('hero_title', 'Sanal Ajanda').parameter,
        'hero_description': general_settings.get('hero_description', 'Sanal Ajanda').parameter,
        'get_started_btn_link': general_settings.get('get_started_btn', '#').description,
        'get_started_btn_text': general_settings.get('get_started_btn', 'Hemen Başlayın').parameter,
        'watch_video_btn_link': general_settings.get('watch_video_btn', '#').description,
        'watch_video_btn_text': general_settings.get('watch_video_btn', 'Videoyu İzle').parameter,
    })

    stats = ['member', 'days', 'notes', 'other']
    for stat in stats:
        context[f'stats_{stat}_num'] = general_settings.get(f'stats_{stat}', '0').parameter
        context[f'stats_{stat}_text'] = general_settings.get(f'stats_{stat}', f'{stat.capitalize()}').description

    for i in range(1, 7):
        context[f'service_{i}_title'] = general_settings.get(f'service_{i}_title', 'Takvim').parameter
        context[f'service_{i}_text'] = general_settings.get(f'service_{i}_text', 'Takvim açıklaması').parameter

    return render(request, 'index.html', context=context)


def get_pricing_settings():
    pricing_settings = PricingSetting.objects.all()

    monthly_plans = []
    yearly_plans = []
    other_settings = {}

    for setting in pricing_settings:
        if setting.name.startswith('month_'):
            monthly_plans.append({
                'id': setting.id,
                'name': setting.name,
                'title': setting.parameter,
                'price': setting.price,
                'features': [setting.feat1, setting.feat2, setting.feat3, setting.feat4, setting.feat5, setting.feat6]
            })
        elif setting.name.startswith('year_'):
            yearly_plans.append({
                'id': setting.id,
                'name': setting.name,
                'title': setting.parameter,
                'price': setting.price,
                'features': [setting.feat1, setting.feat2, setting.feat3, setting.feat4, setting.feat5, setting.feat6]
            })
        else:

            other_settings[setting.name] = setting.parameter

    return {
        'monthly_plans': monthly_plans,
        'yearly_plans': yearly_plans,
        'other_settings': other_settings
    }


def get_faq_settings():
    faq_settings = FaqSetting.objects.all()
    faqs = []
    for faq in faq_settings:
        faqs.append({
            'id': faq.id,
            'name': faq.name,
            'question': faq.question,
            'answer': faq.answer,
        })
    return faqs


def get_navbar_settings():

    navbar_items = NavbarSetting.objects.all()
    return [
        {
            'id': item.id,
            'name': item.name,
            'parameter': item.parameter,
            'link': item.link,
        }
        for item in navbar_items
    ]