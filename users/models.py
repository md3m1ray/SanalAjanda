from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now
from django_otp.models import Device
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.models import User
from model_utils.models import StatusModel, TimeStampedModel
from model_utils import FieldTracker
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User as AuthUser
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for handling email-based authentication.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("E-posta adresi belirtilmelidir.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email instead of username.

    """
    USER_TYPES = [
        ('master', 'Master Kullanıcı'),
        ('secretary', 'Sekreter'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='master')

    MEMBERSHIP_CHOICES = [
        ('standard', 'Başlangıç'),
        ('premium', 'Gümüş'),
        ('pro', 'Altın'),
        ('enterprise', 'Öğrenci'),
    ]

    email = models.EmailField(unique=True, verbose_name="E-posta Adresi")
    first_name = models.CharField(max_length=30, blank=True, verbose_name="Ad")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="Soyad")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Doğum Tarihi")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Telefon Numarası")
    membership_type = models.CharField(
        max_length=15,
        choices=MEMBERSHIP_CHOICES,
        default='standard',
        verbose_name="Üyelik Tipi",
    )
    membership_expiry = models.DateTimeField(null=True, blank=True)
    is_membership_approved = models.BooleanField(
        default=False,
        verbose_name="Üyelik Onayı",
        help_text="Yönetici onayı gerektiren üyelikler için.",
    )
    requested_membership_type = models.CharField(
        max_length=50,
        choices=MEMBERSHIP_CHOICES,
        blank=True,
        null=True
    )

    requested_duration = models.CharField(
        max_length=10,
        choices=[('monthly', '1 Ay'), ('yearly', '1 Yıl')],
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_staff = models.BooleanField(default=False, verbose_name="Personel")
    is_2fa_enabled = models.BooleanField(default=False, verbose_name="2FA")
    email_notifications_enabled = models.BooleanField(
        default=False,
        verbose_name="Email Bildirimlerini Aç/Kapat"
    )
    email_sending_disabled = models.BooleanField(
        default=True,
        verbose_name="Yarın Not olmasa bile E-posta gönderilsin",
    )  # 'not yoksa E-posta gönderilmesin' seçeneği

    # İzlenecek alanları belirtiyoruz
    tracker = FieldTracker(fields=[
        'email_notifications_enabled',
        'is_2fa_enabled',
        'requested_duration',
        'requested_membership_type',
        'is_membership_approved'
    ])

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Superuser creation requires no additional fields


    def is_membership_expired(self):
        """Check if the user's membership has expired."""
        if self.membership_expiry and self.membership_expiry < now():
            return True
        return False

    def is_premium_or_higher(self):
        """
        Check if the user has Premium or higher membership.
        """
        return self.membership_type in ['premium', 'pro', 'enterprise']

    @property
    def is_2fa_enabled(self):
        """Kullanıcı için herhangi bir OTP cihazı olup olmadığını kontrol eder."""
        return (
                StaticDevice.objects.filter(user=self).exists() or
                TOTPDevice.objects.filter(user=self).exists()
        )

    def __str__(self):
        return self.email




    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"


class UserProfile(models.Model):
    """
    Optional user profile for additional information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f"{self.user.email} - Profil"

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"


class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255)  # Kullanıcının yaptığı işlem açıklaması
    timestamp = models.DateTimeField(default=now)  # İşlem zamanı

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.timestamp}"


class Secretary(models.Model):
    master_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="secretaries"
    )
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  # Şifre (hashlenmiş saklanır)

    def save(self, *args, **kwargs):
        if not self.pk:  # Yeni oluşturuluyorsa şifreyi hashle
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


    def __str__(self):
        return f"{self.username} (Üst Kullanıcı: {self.master_user.email})"
