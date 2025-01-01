from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import User, UserActivityLog
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from .models import Secretary


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

    def clean_terms_accepted(self):
        terms_accepted = self.cleaned_data.get('terms_accepted')
        if not terms_accepted:
            raise forms.ValidationError("Devam etmek için şartları okuyup kabul etmelisiniz.")
        return terms_accepted



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


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        label="E-posta",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'E-posta adresinizi giriniz',
            'required': 'required',
        }),

    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi ile kayıtlı bir kullanıcı bulunamadı.")
        return email


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


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'}),
        label="Current Password",
        required=True
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        label="New Password",
        required=True,
        help_text="Password must be at least 8 characters and contain letters and numbers."
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
        label="Confirm New Password",
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password")
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Eski Şifrenizi yanlış girdiniz.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Şifreler Eşleşmiyor")
        return cleaned_data


class MembershipUpgradeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['requested_membership_type', 'requested_duration']
        widgets = {
            'requested_membership_type': forms.Select(attrs={'class': 'form-control'}),
            'requested_duration': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_requested_membership_type(self):
        """Üyelik tipi doğrulama."""
        requested_membership_type = self.cleaned_data.get('requested_membership_type')
        current_type = self.instance.membership_type
        email = self.instance.email

        if not requested_membership_type and current_type == 'standard':
            raise forms.ValidationError("Üyelik tipi seçmelisiniz.")
        if requested_membership_type == 'standard':
            raise forms.ValidationError("Standart üyelik seçilemez.")
        if requested_membership_type == current_type:
            raise forms.ValidationError("Mevcut üyelik tipinizle aynı paketi seçemezsiniz.")
        if requested_membership_type == 'enterprise' and not email.endswith('.edu.tr'):
            raise forms.ValidationError("Öğrenci üyelik tipini seçmek için '@edu.tr' uzantılı bir e-posta adresine sahip olmalısınız.")
        return requested_membership_type

    def clean_requested_duration(self):
        """Üyelik süresi doğrulama."""
        requested_duration = self.cleaned_data.get('requested_duration')
        if not requested_duration:
            raise forms.ValidationError("Üyelik süresi seçmek zorunludur.")
        return requested_duration


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


class ActivityFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Başlangıç Tarihi"
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Bitiş Tarihi"
    )
    action = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="İşlem Türü"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Kullanıcıyı al
        super().__init__(*args, **kwargs)

        if user:
            # Kullanıcının işlemlerine göre dinamik seçimler oluştur
            actions = UserActivityLog.objects.filter(user=user).order_by('action').values_list('action',
                                                                                               flat=True).distinct()
            self.fields['action'].choices = [('', 'Tüm İşlemler')] + [(action, action) for action in actions]


class SecretaryForm(forms.ModelForm):
    class Meta:
        model = Secretary
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.master_user = kwargs.pop('master_user', None)
        super().__init__(*args, **kwargs)

        # Kullanıcı adı düzenleme sırasında sadece ana kısmı gösterilir
        if self.instance and self.instance.pk:
            full_username = self.instance.username
            email_suffix = f"-{self.master_user.email}"
            if full_username.endswith(email_suffix):
                username_without_email = full_username[: -len(email_suffix)]
                self.initial['username'] = username_without_email  # Initial değer
                self.fields['username'].widget.attrs.update({'value': username_without_email})  # Widget value


    def clean_username(self):
        username = self.cleaned_data.get('username')
        full_username = f"{username}-{self.master_user.email}"

        # Mevcut kullanıcı adı hariç aynı kullanıcı adı olup olmadığını kontrol et
        if Secretary.objects.filter(username=full_username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Bu kullanıcı adı zaten mevcut.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        if self.master_user and self.master_user.secretaries.count() >= 3 and not self.instance.pk:
            raise forms.ValidationError("En fazla 3 sekreter oluşturabilirsiniz.")
        return cleaned_data

    def save(self, commit=True):
        # Kullanıcı adı ve şifreyi al
        username = self.cleaned_data.get('username')
        full_username = f"{username}-{self.master_user.email}"  # Tam kullanıcı adı oluştur
        password = self.cleaned_data.get('password')

        # Varolan kullanıcıyı al veya yeni oluştur
        if self.instance.pk and self.instance.user:
            user = self.instance.user  # Mevcut kullanıcıyı al
            user.email = full_username
            if password:  # Şifre değiştiyse
                user.password = make_password(password)
            user.save()
        else:
            # Yeni kullanıcı oluştur
            user = User.objects.create(
                email=full_username,
                password=make_password(password),
                is_active=True,
                user_type='secretary'
            )

        # Secretary modelini kullanıcıyla ilişkilendir
        instance = super().save(commit=False)
        instance.user = user
        instance.username = full_username
        instance.master_user = self.master_user

        if commit:
            instance.save()
        return instance
