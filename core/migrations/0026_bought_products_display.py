# Generated by Django 2.1.1 on 2018-12-17 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_bought_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='bought_products',
            name='display',
            field=models.CharField(blank=True, max_length=128, verbose_name='otobrajat danniye v istorii'),
        ),
    ]