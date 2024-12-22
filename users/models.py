from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    MEMBERSHIP_CHOICES = [
        ('standard', 'Başlangıç'),
        ('premium', 'Gümüş'),
        ('pro', 'Altın'),
        ('enterprise', 'Öğrenci'),
    ]
    membership_type = models.CharField(
        max_length=10,
        choices=MEMBERSHIP_CHOICES,
        default='standard',
        verbose_name="Üyelik Tipi",
    )
    is_membership_approved = models.BooleanField(
        default=False,
        verbose_name="Üyelik Onayı",
        help_text="Yönetici onayı gerektiren üyelikler için.",
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Doğum Tarihi",
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Telefon Numarası",
    )

    def is_premium_or_higher(self):
        """
        Kullanıcının Premium veya daha yüksek bir üyelikte olup olmadığını kontrol eder.
        """
        return self.membership_type in ['premium', 'pro', 'enterprise']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"



# Kullanıcı Profil Ayarları (Opsiyonel)
class UserProfile(models.Model):
    """
    Kullanıcı profili için ek bilgiler.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f"{self.user.username} - Profil"

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"