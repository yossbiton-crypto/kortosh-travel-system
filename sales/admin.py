from django.contrib import admin

from .models import Quote, Request


class QuoteInline(admin.TabularInline):
    model = Quote
    extra = 0
    fields = (
        "quote_type",
        "hotel",
        "tour",
        "bus",
        "vendor_package",
        "composed_package",
        "price",
        "currency",
        "valid_until",
        "is_selected",
    )
    autocomplete_fields = ("hotel", "tour", "bus", "vendor_package", "composed_package")


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code",
        "customer_name",
        "assigned_agent",
        "status",
        "destination",
        "date_from",
        "date_to",
        "created_at",
    )
    list_filter = ("status", "assigned_agent", "destination", "source_channel")
    search_fields = ("reference_code", "customer_name", "customer_email", "customer_phone")
    readonly_fields = ("reference_code", "created_at", "updated_at")
    autocomplete_fields = ("assigned_agent",)
    inlines = [QuoteInline]


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "request",
        "quote_type",
        "price",
        "currency",
        "valid_until",
        "is_selected",
        "created_at",
    )
    list_filter = ("quote_type", "currency", "is_selected")
    search_fields = ("request__reference_code", "request__customer_name")
    autocomplete_fields = ("request", "hotel", "tour", "bus", "vendor_package", "composed_package")
