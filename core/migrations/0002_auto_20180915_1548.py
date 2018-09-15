# Generated by Django 2.1.1 on 2018-09-15 04:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='chat_msg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, verbose_name='Текст')),
            ],
        ),
        migrations.CreateModel(
            name='site_settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_main_spec', models.TextField(blank=True, verbose_name='Название первой категории')),
                ('shop_name', models.TextField(blank=True, verbose_name='Название магазина')),
            ],
        ),
        migrations.AddField(
            model_name='abonent',
            name='telega_id',
            field=models.IntegerField(default=0, verbose_name='ID'),
        ),
        migrations.AddField(
            model_name='raion',
            name='pre_full_name',
            field=models.TextField(blank=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='raion',
            name='subcategory_of',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.raion', verbose_name='Подкатегория от'),
        ),
        migrations.AlterField(
            model_name='abonent',
            name='name',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='product_type',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='raion',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='chat_msg',
            name='abonent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.abonent', verbose_name='Вид'),
        ),
    ]
