# Generated by Django 3.2.12 on 2022-02-28 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TelegramUser",
            fields=[
                ("id", models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ("username", models.CharField(max_length=127, unique=True)),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255, null=True)),
                ("phone", models.CharField(max_length=15, null=True)),
                ("is_bot", models.BooleanField(default=False)),
            ],
        ),
    ]
