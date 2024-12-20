from django.contrib import admin
from contact.models import *


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'subject', 'message', 'updated_date', 'created_date']
    search_fields = ['name', 'email', 'subject', 'message']

    class Meta:
        model = Contact
