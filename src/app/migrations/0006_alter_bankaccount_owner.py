# Generated by Django 3.2.12 on 2022-04-30 09:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_auto_20220411_2137"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bankaccount",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="bank_accounts", to="app.telegramuser"
            ),
        ),
    ]
