# Generated by Django 5.1.4 on 2024-12-31 23:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_useractivitylog'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserActivityLog',
        ),
    ]
