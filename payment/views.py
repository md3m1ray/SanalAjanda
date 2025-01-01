from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import PaymentNotificationForm

def payment_notification(request):
    if request.method == "POST":
        form = PaymentNotificationForm(request.POST)
        if form.is_valid():
            payment = form.save()

            # E-posta bildirimi gönder
            subject = "Yeni Ödeme Bildirimi"
            message = f"""
            Yeni bir ödeme bildirimi aldınız:
            İsim: {payment.first_name} {payment.last_name}
            E-posta: {payment.email}
            Sipariş No: {payment.order_number}
            Ödeme Şekli: {payment.get_payment_method_display()}
            Tutar: {payment.amount} TL
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL]  # Yönetici e-posta adresi
            )

            return redirect('payment_success')  # Başarılı bildirim sonrası yönlendirme
    else:
        form = PaymentNotificationForm()

    return render(request, 'payment/payment_notification.html', {'form': form})
