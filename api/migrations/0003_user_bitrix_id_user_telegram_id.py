# Generated by Django 4.2.2 on 2023-06-21 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_button'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bitrix_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='telegram_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
