# Generated by Django 5.1.4 on 2025-01-03 23:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ajanda', '0002_alter_note_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_notes', to=settings.AUTH_USER_MODEL, verbose_name='Oluşturan Kullanıcı'),
        ),
    ]