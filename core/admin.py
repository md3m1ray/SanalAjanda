from django.contrib import admin

from core.models import *


@admin.register(GeneralSetting)
class GeneralSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'parameter', 'updated_date', 'created_date']
    search_fields = ['name', 'description', 'parameter']
    list_editable = ['description', 'parameter']

    class Meta:
        model = GeneralSetting


@admin.register(NavbarSetting)
class NavbarSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parameter', 'link', 'updated_date', 'created_date']
    search_fields = ['name', 'parameter', 'link']
    list_editable = ['parameter', 'link']

    class Meta:
        model = NavbarSetting


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
    list_editable = ['parameter', 'price', 'feat1', 'feat2', 'feat3', 'feat4', 'feat5', 'feat6']

    class Meta:
        model = FooterSetting


@admin.register(FaqSetting)
class FaqSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'question', 'answer', 'updated_date']
    search_fields = ['name', 'question', 'answer']
    list_editable = ['question', 'answer']

    class Meta:
        model = FaqSetting


@admin.register(ImgUpload)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'image')
    search_fields = ['id', 'title', 'image']
    list_editable = ['title', 'image']

    class Meta:
        model = ImgUpload
