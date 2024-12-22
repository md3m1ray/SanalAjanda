from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


# Özel Kullanıcı Yönetimi
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Kullanıcı yönetimi için özelleştirilmiş admin sınıfı.
    """
    list_display = ['username', 'email', 'membership_type', 'is_membership_approved', 'is_active']
    list_filter = ['membership_type', 'is_membership_approved', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['username']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email', 'date_of_birth', 'phone_number')}),
        ('Üyelik Durumu', {'fields': ('membership_type', 'is_membership_approved')}),
        ('Yetkiler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'membership_type', 'is_membership_approved'),
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
    list_display = ['user',]
    search_fields = ['user__username', 'user__email']
    ordering = ['user']
