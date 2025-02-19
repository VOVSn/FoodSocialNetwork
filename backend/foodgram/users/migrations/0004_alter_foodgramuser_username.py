# Generated by Django 3.2.3 on 2025-02-18 19:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_foodgramuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodgramuser',
            name='username',
            field=models.CharField(help_text='Введите имя пользователя (буквы, цифры, ., @, +, - и _)', max_length=150, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_username', message='Имя пользователя может содержать только буквы, цифры и символы . @ + - _', regex='^[\\w.@+-]+\\Z')], verbose_name='Имя пользователя'),
        ),
    ]
