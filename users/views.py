from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.utils.http import urlsafe_base64_decode
from users.models import User
from django.urls import reverse_lazy
from users.forms import MembershipUpgradeForm
from users.utils import email_verification_token
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from .forms import (LoginForm, RegistrationForm, UserProfileForm, ActivityFilterForm)
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm , SetPasswordForm
from django.contrib.auth.decorators import login_required
from .models import UserActivityLog
from django.utils.timezone import now, timedelta, make_aware, datetime
from .forms import SecretaryForm
from .models import Secretary
from datetime import datetime, timedelta, time
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import get_user_model
from two_factor.utils import default_device
from django.db import connection
from django.contrib.auth.hashers import check_password



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

def login_view(request):
    return redirect('two_factor:login' )

def logout_view(request):
    logout(request)
    messages.success(request, "Başarıyla çıkış yaptınız.")
    return redirect('login')

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

@login_required
def profile(request):
    user = request.user
    membership_type = user.membership_type if hasattr(user, 'membership_type') else 'standard'

    return render(request, 'users/profile.html', {
        'user': user,
        'membership_type': membership_type,
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil bilgileri güncellendi.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})


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
            messages.success(request, "Şifreniz başarıyla güncellendi.")
            return redirect('profile_security')
    else:
        form = SetPasswordForm(user)  # Formu kullanıcıyla başlatın

    return render(request, 'users/profile_security.html', {'form': form})

@login_required
def profile_membership(request):
    if request.method == 'POST':
        form = MembershipUpgradeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_membership_approved = True  # Yönetici onayına ihtiyaç duyuyor
            user.save()
            messages.success(request, "Üyelik yükseltme talebiniz alınmıştır. Yönetici onayı bekleniyor.")
            return redirect('profile_membership')
        else:
            messages.error(request, "Formda hata var. Lütfen tekrar deneyin.")
    else:
        form = MembershipUpgradeForm(instance=request.user)

    return render(request, 'users/profile_membership.html', {'form': form})

@login_required
def toggle_email_notifications(request):
    user = request.user
    user.email_notifications_enabled = not user.email_notifications_enabled
    if not user.email_notifications_enabled:
        user.email_sending_disabled = False
    else:
        user.email_sending_disabled = True
    user.save()
    messages.success(request, "Email bildirim ayarları güncellendi.")
    return redirect('profile_security')

@login_required
def toggle_email_sending(request):
    user = request.user
    user.email_sending_disabled = not user.email_sending_disabled
    user.save()
    messages.success(request, "Not Yok E-Postası için gönderim ayarları güncellendi.")
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

@login_required
def profile_activity(request):
    ten_days_ago = now() - timedelta(days=10)
    activities = UserActivityLog.objects.filter(user=request.user, timestamp__gte=ten_days_ago)

    # Filtreleme
    form = ActivityFilterForm(request.GET, user=request.user)  # Kullanıcıyı form'a geçir
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if start_date:
            # Başlangıç tarihini dahil et
            activities = activities.filter(timestamp__date__gte=start_date)

        if end_date:
            # Bitiş tarihine saat 23:59:59 ekleyerek tüm günü dahil et
            end_datetime = make_aware(datetime.combine(end_date, time.max))
            activities = activities.filter(timestamp__lte=end_datetime)

        if form.cleaned_data['action']:
            activities = activities.filter(action=form.cleaned_data['action'])

        if form.cleaned_data['start_date'] and not form.cleaned_data['end_date']:
            activities = activities.filter(timestamp__date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date'] and not form.cleaned_data['start_date']:
            activities = activities.filter(timestamp__date__lte=form.cleaned_data['end_date'])

    # Sayfalama
    paginator = Paginator(activities.order_by('-timestamp'), 10)  # Her sayfada 10 kayıt
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'users/profile_activity.html', {
        'form': form,
        'page_obj': page_obj,
        'activities': activities
    })

@login_required
def profile_secretaries(request):
    user = request.user  # Giriş yapan kullanıcı

    if request.method == 'POST':
        form = SecretaryForm(request.POST, master_user=user)
        if form.is_valid():
            form.save(commit=True)  # master_user zaten formda atanmış
            messages.success(request, "Sekreter başarıyla eklendi.")
            return redirect('profile_secretaries')
    else:
        form = SecretaryForm(master_user=user)

    secretaries = user.secretaries.all()  # Kullanıcının mevcut sekreterleri

    return render(request, 'users/profile_secretaries.html', {
        'form': form,
        'secretaries': secretaries,
    })

@login_required
def delete_secretary(request, pk):
    user = request.user
    try:
        secretary = user.secretaries.get(pk=pk)  # Sadece kendi sekreterlerini silebilir
        secretary.delete()
        messages.success(request, "Sekreter başarıyla silindi.")
    except Secretary.DoesNotExist:
        messages.error(request, "Sekreter bulunamadı.")
    return redirect('profile_secretaries')

@login_required
def edit_secretary(request, pk):
    user = request.user  # Giriş yapan kullanıcı
    try:
        secretary = user.secretaries.get(pk=pk)  # Sadece kendi sekreterlerini düzenleyebilir
    except Secretary.DoesNotExist:
        messages.error(request, "Sekreter bulunamadı.")
        return redirect('profile_secretaries')

    if request.method == 'POST':
        form = SecretaryForm(request.POST, instance=secretary, master_user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Sekreter başarıyla güncellendi.")
            return redirect('profile_secretaries')
    else:
        form = SecretaryForm(instance=secretary, master_user=user)

    return render(request, 'users/profile_edit_secretary.html', {'form': form, 'secretary': secretary})


User = get_user_model()

class DeleteUserView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'users/delete_account.html')

    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        password = request.POST.get("password")
        google_auth_code = request.POST.get("google_auth_code")
        device = default_device(user)

        if not device:
            messages.error(request, "2FA etkinleştirilmeden bu işlemi gerçekleştiremezsiniz.")
            return redirect('profile_security')  # Kullanıcıyı 2FA ayarlarına yönlendirebilirsiniz

        if request.method == "POST":

            if not device.verify_token(google_auth_code):
                messages.error(request, "Google Authenticator kodu yanlış!")
                return redirect('delete_account')

            if not check_password(password, user.password):
                messages.error(request, "Şifreniz doğru değil!")
                return redirect('delete_account')

            try:
                # Veritabanı işlemlerini bir bütün olarak yürüt
                with connection.cursor() as cursor:
                    # FOREIGN KEY kısıtlamalarını devre dışı bırak
                    cursor.execute("PRAGMA foreign_keys=OFF;")

                    # Kullanıcı ve ilişkili kayıtları sil
                    cursor.execute("DELETE FROM activity_logs WHERE user_id = %s", [user.id])

                    secretaries = Secretary.objects.filter(master_user=user)
                    for secretary in secretaries:
                        # Kullanıcı adıyla eşleşen bir User kaydı varsa sil
                        try:
                            secretary_user = User.objects.get(email=secretary.username, user_type="secretary")
                            secretary_user.delete()
                        except User.DoesNotExist:
                            pass
                    cursor.execute("DELETE FROM secretaries WHERE master_user_id = %s", [user.id])
                    user.delete()
                    # FOREIGN KEY kısıtlamalarını tekrar etkinleştir
                    cursor.execute("PRAGMA foreign_keys=ON;")

                messages.success(request, "Hesabınız ve tüm verileriniz kalıcı olarak silindi.")
                return redirect('login')

            except Exception as e:
                messages.error(request, f"Hesabınızı silerken bir hata oluştu: {str(e)}")
                return redirect('delete_account')