# Generated by Django 2.1.1 on 2018-12-16 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20181216_2048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegram_project',
            name='finance_type',
        ),
    ]