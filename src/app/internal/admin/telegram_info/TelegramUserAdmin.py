from django.contrib import admin

from app.internal.models.telegram_info import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "phone")
    list_display_links = ("id", "username")
    readonly_fields = ("id", "username", "first_name", "last_name", "phone")
