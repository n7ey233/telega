# Generated by Django 2.1.1 on 2018-09-21 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20180920_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='abonent',
            name='transaction_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.product', verbose_name='используется для назначения инстанса при оплате транзакцией'),
        ),
        migrations.AlterField(
            model_name='abonent',
            name='balance',
            field=models.FloatField(default=0, verbose_name='Баланс'),
        ),
        migrations.AlterField(
            model_name='abonent',
            name='telega_id',
            field=models.IntegerField(verbose_name='ID Телеги'),
        ),
    ]
