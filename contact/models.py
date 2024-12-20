from django.db import models

class Contact(models.Model):
    name = models.CharField(
        max_length=150,
        default="",
        blank=False,
        help_text='',
        verbose_name='name'

    )
    email = models.EmailField(
        max_length=150,
        default="",
        blank=False,
        help_text='',
        verbose_name='email'
    )
    subject = models.CharField(
        max_length=150,
        default="",
        blank=False,
        help_text='',
        verbose_name='subject'
    )
    message = models.TextField(
        default="",
        blank=False,
        help_text='',
        verbose_name='message'
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        blank=True
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        blank=True
    )

    def __str__(self):
        return f'Message: {self.name}'

    class Meta:
        verbose_name_plural = "Contacts"
        verbose_name = "Contact"
        ordering = ('id', 'name', 'email', 'subject', 'message', 'updated_date', 'created_date')