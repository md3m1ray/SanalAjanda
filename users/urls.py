from django.urls import path
from users import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    # Kullanıcı işlemleri
    path('register/', views.register, name='register'),  # Kayıt sayfası
    path('login/', views.login_view, name='login'),  # Giriş sayfası
    path('logout/', views.logout_view, name='logout'),  # Çıkış yap
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/security/', views.profile_security, name='profile_security'),
    path('profile/notifications/', views.profile_notifications, name='profile_notifications'),
    path('profile/membership/', views.profile_membership, name='profile_membership'),
    path('profile/activity/', views.profile_activity, name='profile_activity'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password_reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # E-posta doğrulama
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),  # E-posta doğrulama

    # Üyelik yükseltme
    path('upgrade-membership/', views.upgrade_membership, name='upgrade_membership'),  # Üyelik yükseltme

    # Profil ve yönetim
    path('profile/', views.profile, name='profile'),  # Kullanıcı profil sayfası

]
