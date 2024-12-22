from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now

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
        max_length=10,
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
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_staff = models.BooleanField(default=False, verbose_name="Personel")

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
