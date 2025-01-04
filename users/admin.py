from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (User, UserProfile, Secretary, UserActivityLog)
from datetime import timedelta
from django.utils.timezone import now
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice


# Özelleştirilmiş Kullanıcı Yönetimi
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Kullanıcı yönetimi için özelleştirilmiş admin sınıfı.
    """
    list_display = ['email', 'first_name', 'last_name', 'user_type', 'membership_type', 'requested_membership_type', 'requested_duration',
                    'membership_expiry', 'is_membership_approved', 'is_2fa_enabled_display', 'is_active']
    list_filter = ['membership_type', 'is_membership_approved', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'date_of_birth', 'phone_number','email_notifications_enabled','email_sending_disabled')}),
        ('Üyelik Durumu', {'fields': (
        'membership_type', 'requested_membership_type', 'requested_duration', 'membership_expiry',
        'is_membership_approved')}),
        ('Ek Alanlar', {'fields': ('user_type', 'master_user')}),
        ('Yetkiler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'email', 'password1', 'password2', 'membership_type', 'is_membership_approved', 'is_active', 'is_staff'),
        }),
    )
    actions = ['approve_membership']

    @admin.display(boolean=True, description='2FA Enabled')
    def is_2fa_enabled_display(self, obj):
        """Kullanıcının 2FA'nın etkin olup olmadığını kontrol eder."""
        return (
                StaticDevice.objects.filter(user=obj).exists() or
                TOTPDevice.objects.filter(user=obj).exists()
        )


    @admin.action(description="Approve selected membership requests")
    def approve_membership(self, request, queryset):
        for user in queryset:
            if user.requested_membership_type:
                user.membership_type = user.requested_membership_type
                user.requested_membership_type = None
                user.is_membership_approved = False

            if user.requested_duration:
                # Üyelik süresini hesapla
                duration = 30 if user.requested_duration == 'monthly' else 365
                current_time = now()
                if user.membership_expiry:
                    # Eğer `membership_expiry` timezone-aware değilse hata oluşabilir
                    if user.membership_expiry > current_time:
                        user.membership_expiry += timedelta(days=duration)
                    else:
                        user.membership_expiry = current_time + timedelta(days=duration)
                else:
                    user.membership_expiry = current_time + timedelta(days=duration)

                user.requested_duration = None
                user.is_membership_approved = False

            user.save()

        self.message_user(request, "Seçilen üyelikler başarıyla onaylandı.")


# Kullanıcı Profili Yönetimi
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Kullanıcı profili yönetimi için admin sınıfı.
    """
    list_display = ['user']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['user__email']


@admin.register(Secretary)
class SecretaryAdmin(admin.ModelAdmin):
    list_display = ('username', 'master_user')  # Görüntülenecek sütunlar
    search_fields = ('username', 'master_user__username')  # Arama yapılabilir alanlar
    list_filter = ('master_user',)  # Filtre alanları


@admin.register(UserActivityLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('user', 'timestamp')