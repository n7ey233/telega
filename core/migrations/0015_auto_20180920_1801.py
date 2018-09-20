# Generated by Django 2.1.1 on 2018-09-20 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20180920_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abonent',
            name='name',
            field=models.CharField(blank=True, max_length=128, verbose_name='名称为啥，用不用呢？'),
        ),
        migrations.AlterField(
            model_name='product_type',
            name='price',
            field=models.FloatField(default=500, verbose_name='Цена за ед. продукта, если пусто, то дефолту с неё берется ценник на товар'),
        ),
    ]
