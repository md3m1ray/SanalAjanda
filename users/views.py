from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode
from users.models import User
from django.urls import reverse_lazy
from django.views.generic import View
from users.forms import RegistrationForm, MembershipUpgradeForm
from users.utils import email_verification_token
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from .forms import LoginForm, RegistrationForm, UserProfileForm

# Kullanıcı Kayıt
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Kullanıcı pasif, doğrulama bekleniyor
            user.save()
            form.send_verification_email(user)  # Doğrulama e-postası gönder
            messages.success(request, "Kayıt başarılı! Lütfen e-postanızı doğrulayın.")
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})


# Kullanıcı Giriş
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully logged in!")
                return redirect('profile')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


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
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "E-posta doğrulama işlemi başarılı!")
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
            if user.membership_type != 'standard':  # Standart dışı üyelik
                user.is_membership_approved = False  # Onay bekleniyor
            user.save()
            messages.success(request, "Üyelik yükseltme talebiniz alınmıştır. Yönetici onayı bekleniyor.")
            return redirect('profile')
    else:
        form = MembershipUpgradeForm(instance=request.user)
    return render(request, 'users/upgrade_membership.html', {'form': form})


# Profil
@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

# User Profile Edit View
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})

# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
