from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import PaymentNotification

@admin.register(PaymentNotification)
class PaymentNotificationAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'first_name', 'last_name', 'email', 'payment_method', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['order_number', 'first_name', 'last_name', 'email']
    actions = ['mark_as_approved', 'mark_as_rejected']

    def mark_as_approved(self, request, queryset):
        for notification in queryset:
            if notification.status != 'approved':
                # Bildirimi onayla
                notification.status = 'approved'
                notification.save()

                # E-posta gönder
                subject = "Ödeme Bildiriminiz Onaylandı"
                message = f"""
                Sayın {notification.first_name} {notification.last_name},

                Sipariş Numaranız: {notification.order_number}
                Ödeme Şekli: {notification.get_payment_method_display()}
                Tutar: {notification.amount} TL

                Ödemeniz başarıyla onaylanmış ve Paketiniz aktif olmuştur. Teşekkür ederiz!
                """
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [notification.email],
                )


        self.message_user(request, "Seçili bildirimler onaylandı.")
    mark_as_approved.short_description = "Seçili Bildirimleri Onayla"

    def mark_as_rejected(self, request, queryset):
        for notification in queryset:
            if notification.status != 'rejected':
                # Bildirimi reddet
                notification.status = 'rejected'
                notification.save()

                # E-posta gönder
                subject = "Ödeme Bildiriminiz Reddedildi"
                message = f"""
                                Sayın {notification.first_name} {notification.last_name},

                                Sipariş Numaranız: {notification.order_number}
                                Ödeme Şekli: {notification.get_payment_method_display()}
                                Tutar: {notification.amount} TL

                                Ödemeniz yapilmadığı için siparişiniz ve paket isteğiniz reddedilmiştir!
                                """
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [notification.email],
                )


        self.message_user(request, "Seçili bildirimler reddedildi.")
    mark_as_rejected.short_description = "Seçili Bildirimleri Reddet"
