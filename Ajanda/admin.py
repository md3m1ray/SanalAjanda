from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['user','title', 'date', 'time', 'created_at']
    search_fields = ['title', 'user__email']
    list_filter = ['date']
