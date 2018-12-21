# Generated by Django 2.1.1 on 2018-12-21 17:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='abonent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_instance', models.IntegerField(default=0, verbose_name='инстанс платёжки')),
                ('telega_id', models.IntegerField(verbose_name='ID Телеги')),
                ('balance', models.FloatField(default=0, verbose_name='Баланс')),
                ('name', models.CharField(blank=True, max_length=128, verbose_name='名称为啥，用不用呢？')),
                ('job_seeker', models.BooleanField(default=False, verbose_name='Ищет работу')),
                ('support_seeker', models.BooleanField(default=False, verbose_name='Ждет связи с оператором')),
            ],
            options={
                'ordering': ['telega_id'],
            },
        ),
        migrations.CreateModel(
            name='bought_products',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128, verbose_name='tuple s dannimi o pokupke')),
                ('display', models.CharField(blank=True, max_length=128, verbose_name='otobrajat danniye v istorii')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('abonent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.abonent', verbose_name='Пополнитель(из телеги)')),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='chat_msg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, verbose_name='Текст')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('abonent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.abonent', verbose_name='Вид')),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='finished_transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('paid_transaction', models.BooleanField(default=False, verbose_name='Оплачено')),
                ('txnId', models.CharField(blank=True, max_length=128, verbose_name='Номер транзакции')),
                ('cash', models.FloatField(default=0, verbose_name='Сумма')),
                ('abonent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.abonent', verbose_name='Пополнитель(из телеги)')),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('sold_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата продажи')),
                ('price', models.FloatField(blank=True, null=True, verbose_name='Цена, если пусто, то ценник берется с вида продукции')),
                ('commentary', models.TextField(null=True, verbose_name='Дополнительное описание')),
                ('geolocation', models.URLField(max_length=256, null=True, verbose_name='Ссылка на геолокацию')),
                ('foto_link', models.URLField(max_length=256, null=True, verbose_name='Ссылка на фото')),
                ('buyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.abonent', verbose_name='Покупатель')),
            ],
            options={
                'ordering': ['created_date'],
            },
        ),
        migrations.CreateModel(
            name='product_type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Название')),
                ('price', models.FloatField(default=500, verbose_name='Цена за ед. продукта, если пусто, то дефолту с неё берется ценник на товар')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='raion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pre_full_name', models.TextField(blank=True, verbose_name='префикс, используется для отображения')),
                ('name', models.CharField(max_length=128, verbose_name='Название')),
                ('subcategory_of', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.raion', verbose_name='Подкатегория от')),
            ],
            options={
                'ordering': ['pre_full_name'],
            },
        ),
        migrations.CreateModel(
            name='site_settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_main_spec', models.CharField(blank=True, max_length=128, verbose_name='Название первой категории')),
                ('shop_name', models.CharField(blank=True, max_length=128, verbose_name='Название магазина')),
                ('tele_token', models.CharField(blank=True, max_length=128, verbose_name='токен телеги')),
                ('qiwi_token', models.CharField(blank=True, max_length=128, verbose_name='токен киви')),
                ('qiwi_wallet_num', models.CharField(blank=True, max_length=128, verbose_name='номер киви')),
            ],
        ),
        migrations.CreateModel(
            name='telegram_project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_type', models.CharField(choices=[('tg_shop_fake', 'tg_shop_fake')], default='tg_shop_fake', max_length=22, verbose_name='Тип телеги')),
                ('tg_token', models.CharField(max_length=128, verbose_name='tg_token')),
                ('tg_id', models.CharField(blank=True, max_length=128, verbose_name='tg_id, 为了看清楚')),
                ('tg_username', models.CharField(blank=True, max_length=128, verbose_name='tg_username, 为了看清楚')),
                ('tg_first_name', models.CharField(blank=True, max_length=128, verbose_name='tg_first_name, 为了看清楚')),
                ('web_hook_chained', models.BooleanField(default=False, verbose_name='вебхук')),
                ('start_word', models.CharField(max_length=128, verbose_name='стартовая фраза')),
            ],
            options={
                'ordering': ['tg_username'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='placing',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.raion', verbose_name='Место хранения'),
        ),
        migrations.AddField(
            model_name='product',
            name='type_of_product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.product_type', verbose_name='Вид товара'),
        ),
        migrations.AddField(
            model_name='finished_transaction',
            name='project_fk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.telegram_project', verbose_name='project_fk'),
        ),
        migrations.AddField(
            model_name='abonent',
            name='fake_purchases',
            field=models.ManyToManyField(blank=True, related_name='fake_one', to='core.product', verbose_name='Список транзакциий апп'),
        ),
        migrations.AddField(
            model_name='abonent',
            name='transaction_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.product', verbose_name='используется для назначения инстанса при оплате транзакцией'),
        ),
    ]
