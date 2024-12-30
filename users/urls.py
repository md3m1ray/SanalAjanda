from django.urls import path
from users import views
from .views import (toggle_email_notifications, change_password, disable_two_factor,
                    toggle_email_sending, profile_secretaries, delete_secretary, edit_secretary)

urlpatterns = [
    # Kullanıcı işlemleri
    path('register/', views.register, name='register'),  # Kayıt sayfası
    path('login/', views.login_view, name='login'),
    path('disable-two-factor/', disable_two_factor, name='disable_two_factor'),
    path('logout/', views.logout_view, name='logout'),  # Çıkış yap
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/security/', views.profile_security, name='profile_security'),
    path('toggle-email-notifications/', toggle_email_notifications, name='toggle_email_notifications'),
    path('toggle-email-sending/', toggle_email_sending, name='toggle_email_sending'),
    path('profile/membership/', views.profile_membership, name='profile_membership'),
    path('profile/activity/', views.profile_activity, name='profile_activity'),
    path('profile/secretaries/', views.profile_secretaries, name='profile_secretaries'),
    path('profile/secretaries/delete/<int:pk>/', delete_secretary, name='delete_secretary'),
    path('profile/secretaries/edit/<int:pk>/', edit_secretary, name='edit_secretary'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password_reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # E-posta doğrulama
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),  # E-posta doğrulama
    # Profil ve yönetim
    path('profile/', views.profile, name='profile'),  # Kullanıcı profil sayfası
    path('change_password/', change_password, name='change_password'),

]
