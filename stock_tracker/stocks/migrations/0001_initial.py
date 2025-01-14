# Generated by Django 5.1.4 on 2025-01-06 07:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SCRIP', models.CharField(max_length=100)),
                ('WACC', models.FloatField(default=0)),
                ('Purchased_Date', models.DateField(blank=True, null=True)),
                ('Interest_Rate', models.FloatField(default=0)),
                ('Quantity', models.IntegerField(default=0)),
                ('LTP', models.FloatField(default=0)),
                ('Sold', models.BooleanField(default=False)),
                ('Sellable', models.BooleanField(default=True)),
                ('Sold_At', models.FloatField(blank=True, null=True)),
                ('Sold_Date', models.DateField(blank=True, null=True)),
                ('Broker_Commission', models.FloatField(default=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
