# Generated by Django 2.1.1 on 2018-09-15 08:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_abonent_payment_instance'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='placing',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.raion', verbose_name='район хранения'),
        ),
        migrations.AlterField(
            model_name='raion',
            name='pre_full_name',
            field=models.TextField(blank=True, verbose_name='префикс, используется для отображения'),
        ),
    ]
