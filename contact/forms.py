from django import forms
from django.conf import settings
from django.core.mail import EmailMessage


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        required=True,
    )
    email = forms.EmailField(
        max_length=150,
        required=True,
    )
    subject = forms.CharField(
        max_length=150,
        required=True,
    )
    message = forms.CharField(
        widget=forms.Textarea,
        required=True,
    )

    def send_mail(self):
        if self.is_valid():
            name = f'{self.cleaned_data["name"]}'
            email = f'{self.cleaned_data["email"]}'
            subject = f'{self.cleaned_data["subject"]}'
            message = f'{self.cleaned_data["message"]}'
            message_context = (
                'Destek Mesajı Alındı. \n\n'
                f'Name: {name}\n\n'
                f'Email: {email}\n\n'
                f'Subject: {subject}\n\n'
                f'Message: {message}\n\n'
            )

            email_message = EmailMessage(
                subject=subject,
                body=message_context,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],
                reply_to=[email],
            )
            email_message.send()
