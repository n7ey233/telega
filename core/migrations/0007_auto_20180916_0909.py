# Generated by Django 2.1.1 on 2018-09-15 22:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20180915_1903'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='raion',
            options={'ordering': ['pre_full_name']},
        ),
        migrations.AlterField(
            model_name='product',
            name='placing',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.raion', verbose_name='Место хранения'),
        ),
    ]
