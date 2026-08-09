from django.contrib import admin

from .models import Bus, ComposedPackage, Hotel, Tour, VendorPackage


class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "supplier_name",
        "price",
        "currency",
        "available_from",
        "available_to",
        "quantity_available",
        "is_active",
    )
    list_filter = ("is_active", "currency", "supplier_name")
    search_fields = ("name", "supplier_name")
    date_hierarchy = "available_from"


@admin.register(Hotel)
class HotelAdmin(InventoryItemAdmin):
    list_display = InventoryItemAdmin.list_display + ("city", "star_rating", "board_basis")
    list_filter = InventoryItemAdmin.list_filter + ("city", "star_rating", "board_basis")


@admin.register(Tour)
class TourAdmin(InventoryItemAdmin):
    list_display = InventoryItemAdmin.list_display + ("duration_hours", "language")


@admin.register(Bus)
class BusAdmin(InventoryItemAdmin):
    list_display = InventoryItemAdmin.list_display + ("vehicle_type", "seat_capacity")


@admin.register(VendorPackage)
class VendorPackageAdmin(InventoryItemAdmin):
    list_display = InventoryItemAdmin.list_display + (
        "includes_hotel",
        "includes_transfer",
        "includes_tour",
        "nights",
    )
    list_filter = InventoryItemAdmin.list_filter + (
        "includes_hotel",
        "includes_transfer",
        "includes_tour",
    )


@admin.register(ComposedPackage)
class ComposedPackageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "hotel",
        "tour",
        "bus",
        "hotel_price",
        "tour_price",
        "bus_price",
        "total_price",
        "currency",
    )
    readonly_fields = ("total_price", "created_at", "updated_at")
    search_fields = ("name",)
    autocomplete_fields = ("hotel", "tour", "bus")
