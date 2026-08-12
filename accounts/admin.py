from django.contrib import admin

from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "vendor_category", "phone", "is_active")
    list_filter = ("vendor_category", "is_active")
    search_fields = ("display_name", "user__username", "user__email", "phone")
    autocomplete_fields = ("user",)
