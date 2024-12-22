from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


# Özelleştirilmiş Kullanıcı Yönetimi
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Kullanıcı yönetimi için özelleştirilmiş admin sınıfı.
    """
    list_display = ['email', 'first_name', 'last_name', 'membership_type', 'membership_expiry', 'is_membership_approved', 'is_active']
    list_filter = ['membership_type', 'is_membership_approved', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'date_of_birth', 'phone_number')}),
        ('Üyelik Durumu', {'fields': ('membership_type', 'membership_expiry', 'is_membership_approved')}),
        ('Yetkiler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'membership_type', 'is_membership_approved', 'is_active', 'is_staff'),
        }),
    )
    actions = ['approve_memberships']

    @admin.action(description="Seçili üyelikleri onayla")
    def approve_memberships(self, request, queryset):
        """
        Seçilen kullanıcıların üyeliklerini onaylar.
        """
        queryset.update(is_membership_approved=True)
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
