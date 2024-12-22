from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from .models import User
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


# Kullanıcı Kayıt Formu
class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Ad",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Soyad",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        required=True,
        label="E-posta",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="Doğru bir e-posta adresi giriniz.",
    )
    membership_type = forms.ChoiceField(
        choices=User.MEMBERSHIP_CHOICES,
        initial='standard',
        label="Üyelik Tipi",
    )
    terms_accepted = forms.BooleanField(
        label="Şartları ve koşulları kabul ediyorum.",
        required=True,
        error_messages={'required': "Devam etmek için şartları kabul etmelisiniz."},
    )
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def clean(self):
        cleaned_data = super().clean()
        # Ek doğrulamalar ekleyebilirsiniz
        return cleaned_data


    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'membership_type']



    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kayıtlı.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Kullanıcı e-posta doğrulama yapana kadar pasif
        if commit:
            user.save()
            self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        """Kayıt sonrası doğrulama e-postası gönderme."""
        from django.core.mail import send_mail
        from django.conf import settings
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.urls import reverse
        from .utils import email_verification_token

        subject = "E-posta Doğrulama"
        token = email_verification_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = f"{settings.SITE_URL}{reverse('verify_email', kwargs={'uidb64': uid, 'token': token})}"

        message = f"Merhaba {user.first_name},\n\n"
        message += f"Lütfen e-posta adresinizi doğrulamak için aşağıdaki bağlantıya tıklayın:\n\n{verification_url}\n\n"
        message += "Teşekkürler!"

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])



# Şifre Sıfırlama Formu
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        label="E-posta",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="Kayıtlı e-posta adresinizi girin.",
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi ile kayıtlı bir kullanıcı bulunamadı.")
        return email


# Yeni Şifre Belirleme Formu
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Yeni Şifre",
        help_text="Güçlü bir şifre oluşturun.",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Yeni Şifre (Tekrar)",
        help_text="Yeni şifrenizi tekrar girin.",
    )


# Üyelik Yükseltme Formu
class MembershipUpgradeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['membership_type']
        widgets = {
            'membership_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_membership_type(self):
        membership_type = self.cleaned_data.get('membership_type')
        if membership_type != 'standard' and not self.instance.is_membership_approved:
            raise forms.ValidationError("Üyelik yükseltme talebi yönetici onayı bekliyor.")
        return membership_type


# Profil Güncelleme Formu
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(
        required=False,
        label="Beni hatırla",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))