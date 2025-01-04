from django.db import models
from users.models import User
from sanalAjanda import settings
from cryptography.fernet import Fernet

cipher = Fernet(settings.ENCRYPTION_KEY)

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=255, verbose_name="Başlık")
    content = models.TextField(verbose_name="İçerik")
    date = models.DateField(verbose_name="Tarih")
    time = models.TimeField(null=True, blank=True, verbose_name="Saat")
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='created_notes',
        verbose_name='Oluşturan Kullanıcı',
        null=True,  # Eski notlar için
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    def save(self, *args, **kwargs):

        # Master kullanıcıya not kaydetme
        if self.user.user_type == "secretary" and self.user.master_user:
            self.user = self.user.master_user

        # İçeriği şifrele
        if not self.pk:  # Yeni bir not ise
            cipher = Fernet(settings.ENCRYPTION_KEY)
            self.content = cipher.encrypt(self.content.encode()).decode()

            # `created_by` alanını ayarla
            if not self.created_by:
                self.created_by = self.user

        super().save(*args, **kwargs)

    def get_content(self):
        # Şifre çözme işlemi
        try:
            return cipher.decrypt(self.content.encode()).decode()
        except Exception as e:
            return f"Şifre çözme hatası: {str(e)}"

    def __str__(self):
        return f"{self.title} - {self.user.email}"
