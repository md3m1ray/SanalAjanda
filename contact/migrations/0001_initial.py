# Generated by Django 5.1.4 on 2024-12-27 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=150, verbose_name='name')),
                ('email', models.EmailField(default='', max_length=150, verbose_name='email')),
                ('subject', models.CharField(default='', max_length=150, verbose_name='subject')),
                ('message', models.TextField(default='', verbose_name='message')),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
                'ordering': ('id', 'name', 'email', 'subject', 'message', 'updated_date', 'created_date'),
            },
        ),
    ]
