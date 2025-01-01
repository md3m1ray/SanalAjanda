from django.urls import path
from django.views.generic import TemplateView

from .views import payment_notification

urlpatterns = [
    path('payment-notification/', payment_notification, name='payment_notification'),
    path('payment-success/', TemplateView.as_view(template_name='payment/payment_success.html'), name='payment_success'),
]
