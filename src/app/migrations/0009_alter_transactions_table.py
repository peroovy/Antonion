# Generated by Django 3.2.13 on 2022-06-13 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0008_create_secret_key"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="adminuser",
            options={"verbose_name": "user", "verbose_name_plural": "users"},
        ),
        migrations.AddField(
            model_name="transaction",
            name="photo",
            field=models.ImageField(default=None, null=True, upload_to="transactions/%Y/%m/%d/"),
        ),
        migrations.AddField(
            model_name="transaction",
            name="was_destination_viewed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="transaction",
            name="was_source_viewed",
            field=models.BooleanField(default=False),
        ),
    ]
