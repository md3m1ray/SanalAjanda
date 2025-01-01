from django import forms
from .models import PaymentNotification

class PaymentNotificationForm(forms.ModelForm):
    class Meta:
        model = PaymentNotification
        fields = ['first_name', 'last_name', 'email', 'order_number', 'payment_method', 'amount']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İsim'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyisim'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta'}),
            'order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sipariş No'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ödeme Tutarı'}),
        }
