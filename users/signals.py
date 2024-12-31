from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from .models import User, Secretary, UserActivityLog
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.conf import settings
from django.db import transaction


@receiver(post_save, sender=User)
def log_user_update(sender, instance, created, **kwargs):
    if hasattr(instance, 'secretary_profile'):
        return
    if created:
        action = "Yeni kullanıcı oluşturuldu."
        UserActivityLog.objects.create(user=instance, action=action)

@receiver(pre_save, sender=User)
def log_user_profile_changes(sender, instance, **kwargs):
    if hasattr(instance, 'secretary_profile'):
        return
    if instance.pk:  # Kullanıcı zaten varsa (güncelleme işlemi)
        old_instance = sender.objects.get(pk=instance.pk)

        # İsim değişikliği
        if old_instance.first_name != instance.first_name:
            action = f"Ad değiştirildi: '{old_instance.first_name}' -> '{instance.first_name}'."
            UserActivityLog.objects.create(user=instance, action=action)

        # Soyisim değişikliği
        if old_instance.last_name != instance.last_name:
            action = f"Soyad değiştirildi: '{old_instance.last_name}' -> '{instance.last_name}'."
            UserActivityLog.objects.create(user=instance, action=action)

        # E-posta değişikliği
        if old_instance.email != instance.email:
            action = f"E-posta değiştirildi: '{old_instance.email}' -> '{instance.email}'."
            UserActivityLog.objects.create(user=instance, action=action)

        # Şifre değişikliği
        if old_instance.password != instance.password:
            action = "Şifre değiştirildi."
            UserActivityLog.objects.create(user=instance, action=action)

@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    if hasattr(instance, 'secretary_profile'):
        return
    action = "Kullanıcı silindi."
    UserActivityLog.objects.create(user=instance, action=action)

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    if hasattr(user, 'secretary_profile'):
        return
    UserActivityLog.objects.create(user=user, action="Oturum açıldı.")

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if hasattr(user, 'secretary_profile'):
        return
    UserActivityLog.objects.create(user=user, action="Oturum kapatıldı.")

@receiver(post_save, sender=User)
def log_email_notification_toggle(sender, instance, **kwargs):
    if hasattr(instance, 'secretary_profile'):
        return
    if instance.tracker.has_changed('email_notifications_enabled'):
        previous_state = instance.tracker.previous('email_notifications_enabled')
        current_state = instance.email_notifications_enabled
        action = (
            "E-posta bildirimleri açıldı."
            if current_state
            else "E-posta bildirimleri kapatıldı."
        )
        UserActivityLog.objects.create(user=instance, action=action)

@receiver(post_save, sender=User)
def log_two_factor_toggle(sender, instance, **kwargs):
    if hasattr(instance, 'secretary_profile'):
        return
    if instance.tracker.has_changed('is_2fa_enabled'):
        current_state = instance.is_2fa_enabled
        action = (
            "2FA (İki Faktörlü Doğrulama) etkinleştirildi."
            if current_state
            else "2FA devre dışı bırakıldı."
        )
        UserActivityLog.objects.create(user=instance, action=action)

@receiver(post_save, sender=User)
def log_membership_extension_request(sender, instance, **kwargs):
    if hasattr(instance, 'secretary_profile'):
        return
    if instance.tracker.has_changed('requested_duration') and instance.requested_duration != None:
        duration_display = instance.get_requested_duration_display()
        action = f"Üyelik süresi uzatma talep edildi: {duration_display}."
        UserActivityLog.objects.create(user=instance, action=action)

@receiver(post_save, sender=User)
def log_membership_package_request(sender, instance, **kwargs):
    if hasattr(instance, 'secretary_profile'):
        return
    if instance.tracker.has_changed('requested_membership_type'):
        membership_display = instance.get_requested_membership_type_display()
        action = f"Üyelik paketi talep edildi: {membership_display}."
        UserActivityLog.objects.create(user=instance, action=action)

@receiver(post_save, sender=User)
def log_membership_package_approval(sender, instance, **kwargs):
    if hasattr(instance, 'secretary_profile'):
        return
    if instance.tracker.has_changed('is_membership_approved'):
        previous_state = instance.tracker.previous('is_membership_approved')
        current_state = instance.is_membership_approved
        action = (
            "Üyelik paketi onay bekliyor."
            if current_state
            else "Üyelik paketi onaylandı."
        )
        UserActivityLog.objects.create(user=instance, action=action)

@receiver(post_save, sender=Secretary)
def log_secretary_save(sender, instance, created, **kwargs):
    if hasattr(instance, 'secretary_profile'):
        return
    if created:
        action = f"Sekreter eklendi: {instance.username}"
    else:
        action = f"Sekreter düzenlendi: {instance.username}"
    UserActivityLog.objects.create(user=instance.master_user, action=action)

@receiver(post_delete, sender=Secretary)
def log_secretary_delete(sender, instance, **kwargs):
    if hasattr(instance, 'secretary_profile'):
        return
    action = f"Sekreter silindi: {instance.username}"
    UserActivityLog.objects.create(user=instance.master_user, action=action)

@receiver(post_delete, sender=Secretary)
def delete_user_on_secretary_delete(sender, instance, **kwargs):
    if instance.user:
       instance.user.delete()  # İlgili User nesnesini sil