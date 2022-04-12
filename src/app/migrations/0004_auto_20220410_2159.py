# Generated by Django 3.2.12 on 2022-04-10 16:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_auto_20220319_1616"),
    ]

    operations = [
        migrations.AddField(
            model_name="telegramuser",
            name="friends",
            field=models.ManyToManyField(to="app.TelegramUser"),
        ),
        migrations.AlterField(
            model_name="bankcard",
            name="bank_account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="bank_cards", to="app.bankaccount"
            ),
        ),
    ]