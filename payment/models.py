from django.db import models
from django.utils.translation import gettext_lazy as _

class PaymentNotification(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Kredi Kartı'),
        ('bank_transfer', 'Banka Havalesi'),
        ('other', 'Diğer'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Onay Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]

    first_name = models.CharField(max_length=50, verbose_name="İsim")
    last_name = models.CharField(max_length=50, verbose_name="Soyisim")
    email = models.EmailField(verbose_name="E-posta")
    order_number = models.CharField(max_length=50, verbose_name="Sipariş No")
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Ödeme Şekli"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ödeme Tutarı")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Durum"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Bildirim Tarihi")

    def __str__(self):
        return f"{self.order_number} - {self.first_name} {self.last_name} - {self.get_status_display()}"
