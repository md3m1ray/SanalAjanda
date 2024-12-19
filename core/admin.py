from django.contrib import admin

from core.models import *


@admin.register(GeneralSetting)
class GeneralSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'parameter', 'updated_date', 'created_date']
    search_fields = ['name', 'description', 'parameter']
    list_editable = ['description', 'parameter']

    class Meta:
        model = GeneralSetting


@admin.register(FooterSetting)
class FooterSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'parameter', 'link', 'updated_date', 'created_date']
    search_fields = ['name', 'description', 'parameter', 'link']
    list_editable = ['description', 'parameter', 'link']

    class Meta:
        model = FooterSetting


@admin.register(PricingSetting)
class PricingSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parameter', 'price', 'feat1', 'feat2', 'feat3', 'feat4', 'feat5', 'feat6',
                    'updated_date']
    search_fields = ['name', 'parameter']
    list_editable = ['parameter', 'price', 'feat1', 'feat2', 'feat3', 'feat4', 'feat5', 'feat6' ]

    class Meta:
        model = FooterSetting


@admin.register(FaqSetting)
class FaqSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'question', 'answer', 'updated_date']
    search_fields = ['name', 'question', 'answer']
    list_editable = ['question', 'answer']

    class Meta:
        model = FaqSetting