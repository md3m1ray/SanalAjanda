from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode
from users.models import User
from django.urls import reverse_lazy
from users.forms import MembershipUpgradeForm
from users.utils import email_verification_token
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from .forms import LoginForm, RegistrationForm, UserProfileForm
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm , SetPasswordForm

from django.contrib.auth.decorators import login_required


# Kullanıcı Kayıt
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Kullanıcı pasif, doğrulama bekleniyor
            user.save()
            try:
                form.send_verification_email(user)  # Doğrulama e-postası gönder
                messages.success(request, "Kayıt başarılı! Lütfen e-postanızı doğrulayın.")
            except Exception as e:
                messages.error(request, f"E-posta gönderiminde hata oluştu. Lütfen tekrar Deneyiniz")
                user.delete()  # Kullanıcı kaydını geri al
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})


# Kullanıcı Giriş
def login_view(request):
    return redirect('two_factor:login' )


# Kullanıcı Çıkış
def logout_view(request):
    logout(request)
    messages.success(request, "Başarıyla çıkış yaptınız.")
    return redirect('login')


# E-posta Doğrulama
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Geçersiz kullanıcı veya bağlantı hatası.")
        return redirect('login')

    if email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "E-posta doğrulama başarılı! Artık giriş yapabilirsiniz.")
    else:
        messages.error(request, "Doğrulama bağlantısı geçersiz veya süresi dolmuş.")
    return redirect('login')


# Üyelik Yükseltme Talebi
@login_required
def upgrade_membership(request):
    if request.method == 'POST':
        form = MembershipUpgradeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_membership_approved = True  # Yönetici onayına ihtiyaç duyuyor
            user.save()
            messages.success(request, "Üyelik yükseltme talebiniz alınmıştır. Yönetici onayı bekleniyor.")
            return redirect('profile')
        else:
            messages.error(request, "Formda hata var. Lütfen tekrar deneyin.")
    else:
        form = MembershipUpgradeForm(instance=request.user)

    return render(request, 'users/upgrade_membership.html', {'form': form})

# Profil
@login_required
def profile(request):
    user = request.user
    membership_type = user.membership_type if hasattr(user, 'membership_type') else 'standard'

    return render(request, 'users/profile.html', {
        'user': user,
        'membership_type': membership_type,
    })



# User Profile Edit View
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})


# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'

@login_required
def profile_security(request):
    user = request.user  # Oturum açmış kullanıcı
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)  # Kullanıcıyı form ile başlatın
        if form.is_valid():
            form.save()  # Yeni şifreyi kaydet
            update_session_auth_hash(request, user)  # Kullanıcının oturumunu açık tut
            messages.success(request, "Your password has been successfully updated.")
            return redirect('profile_security')
    else:
        form = SetPasswordForm(user)  # Formu kullanıcıyla başlatın

    return render(request, 'users/profile_security.html', {'form': form})

@login_required
def profile_notifications(request):
    return render(request, 'users/profile_notifications.html', )

@login_required
def profile_membership(request):
    return render(request, 'users/profile_membership.html', )

@login_required
def profile_activity(request):
    return render(request, 'users/profile_activity.html', )

@login_required
def toggle_email_notifications(request):
    user = request.user
    user.email_notifications_enabled = not user.email_notifications_enabled
    user.save()
    messages.success(request, "Email bildirim ayarları güncellendi.")
    return redirect('profile_security')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, "Şifreniz Başarıyla Değiştirildi.")
            return redirect('profile_security')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/profile_security.html', {'form': form})

@login_required
def disable_two_factor(request):
    """Kullanıcının 2FA cihazlarını kaldır."""
    TOTPDevice.objects.filter(user=request.user).delete()
    if not request.user.is_2fa_enabled:
        messages.success(request, "Two-Factor Authentication başarıyla devre dışı bırakıldı.")
    else:
        messages.error(request, "Two-Factor Authentication devre dışı bırakılamadı. Lütfen tekrar deneyin.")
    return redirect('profile_security')