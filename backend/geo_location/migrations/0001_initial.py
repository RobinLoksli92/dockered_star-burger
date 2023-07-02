# Generated by Django 3.2 on 2022-07-31 11:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeoLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200, verbose_name='Адрес')),
                ('lat', models.IntegerField(null=True, verbose_name='Широта')),
                ('long', models.IntegerField(null=True, verbose_name='Долгота')),
                ('request_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата запроса к геокодеру')),
            ],
        ),
    ]