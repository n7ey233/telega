# Generated by Django 2.1.1 on 2018-12-21 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20181222_0310'),
    ]

    operations = [
        migrations.AddField(
            model_name='raion',
            name='latitude',
            field=models.CharField(blank=True, max_length=128, verbose_name='latitude'),
        ),
        migrations.AddField(
            model_name='raion',
            name='longitude',
            field=models.CharField(blank=True, max_length=128, verbose_name='longitude'),
        ),
    ]
