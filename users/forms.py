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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_first_name',
            'placeholder': 'Adınız',
            'required': 'required'
        }),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_last_name',
            'placeholder': 'Soyadınız',
            'required': 'required'
        }),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'id_email',
            'placeholder': 'Email Adresiniz',
            'required': 'required'
        }),
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_password1',
            'placeholder': 'Şifre',
            'required': 'required'
        }),
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_password2',
            'placeholder': 'Şifre (Tekrar)',
            'required': 'required'
        }),
    )
    membership_type = forms.ChoiceField(
        required=True,
        choices=[('', 'Select your membership type')] + User.MEMBERSHIP_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_membership_type',
            'required': 'required',
        }),
    )

    requested_duration = forms.ChoiceField(
        choices=[('', 'Talep Edilen Süre'), ('monthly', '1 Ay'), ('yearly', '1 Yıl')],
        required=False,
        label="Talep Edilen Süre",
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
    )
    terms_accepted = forms.BooleanField(
        required=True,
        disabled=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'agree-term',
            'required': 'required'
        }),
        error_messages={'required': "Devam etmek için şartları okuyup kabul etmelisiniz."},
    )
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def clean(self):
        cleaned_data = super().clean()
        membership_type = cleaned_data.get('membership_type')
        requested_duration = cleaned_data.get('requested_duration')

        if membership_type != 'standard' and not requested_duration:
            raise forms.ValidationError("Üyelik tipi seçildiğinde 'Talep Edilen Süre' zorunludur.")

        return cleaned_data


    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'membership_type', 'requested_duration']



    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kayıtlı.")
        return email

    def clean_membership_type(self):
        membership_type = self.cleaned_data.get('membership_type')
        email = self.cleaned_data.get('email')

        if membership_type == 'enterprise' and (not email or not email.endswith('.edu.tr')):
            raise forms.ValidationError(
                "Öğrenci üyelik tipini seçebilmek için '@edu.tr' uzantılı bir e-posta adresine sahip olmalısınız.")
        return membership_type

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Kullanıcı e-posta doğrulama yapana kadar pasif
        user.requested_membership_type = self.cleaned_data[
            'membership_type']  # Seçilen üyelik türü talep olarak kaydedilir
        user.requested_duration = self.cleaned_data.get('requested_duration')
        user.membership_type = 'standard'  # Üyelik tipi varsayılan olarak "standart"
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
from django import forms
from users.models import User


# Üyelik Yükseltme Formu
class MembershipUpgradeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['requested_membership_type', 'requested_duration']
        widgets = {
            'requested_membership_type': forms.Select(attrs={'class': 'form-control'}),
            'requested_duration': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_membership_type(self):
        cleaned_data = super().clean()
        requested_membership_type = cleaned_data.get('requested_membership_type')
        requested_duration = cleaned_data.get('requested_duration')
        current_type = self.instance.membership_type
        email = self.instance.email

        if current_type == 'standard':
            # Eğer kullanıcı "standard" üyelikteyse, hem üyelik tipi hem de süre zorunlu
            if not requested_membership_type:
                raise forms.ValidationError("Üyelik tipi seçmelisiniz.")
            if not requested_duration:
                raise forms.ValidationError("Üyelik süresi seçmelisiniz.")
            if requested_membership_type == 'enterprise' and not email.endswith('@edu.tr'):
                raise forms.ValidationError(
                    "Öğrenci üyelik tipini seçebilmek için '@edu.tr' uzantılı bir e-posta adresine sahip olmalısınız.")
        else:
            # Eğer kullanıcının zaten aktif bir üyeliği varsa, sadece süre uzatma yapılabilir
            if not requested_duration:
                raise forms.ValidationError("Süre uzatma talebi için süre seçmelisiniz.")
            if requested_membership_type and requested_membership_type != current_type:
                raise forms.ValidationError("Mevcut üyelik türünüzü değiştiremezsiniz.")
        return cleaned_data


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