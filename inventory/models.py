from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Currency(models.TextChoices):
    EUR = "EUR", "EUR"
    USD = "USD", "USD"
    HUF = "HUF", "HUF"
    ILS = "ILS", "ILS"


class InventoryItem(models.Model):
    """Shared fields for a single-layer inventory offering (hotel/tour/bus).

    Each row is one bookable offering from one supplier: it carries its own
    price, availability window and basic sales terms so it can be quoted
    on its own or combined into a composed package.
    """

    name = models.CharField(max_length=200)
    supplier_name = models.CharField(
        max_length=200, help_text="The vendor/company this offering is bought from."
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.EUR
    )
    available_from = models.DateField()
    available_to = models.DateField()
    quantity_available = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Rooms/seats/slots available, if capacity-limited.",
    )
    terms = models.TextField(
        blank=True,
        help_text="Cancellation policy, payment terms, inclusions, etc.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.supplier_name})"

    def clean(self):
        super().clean()
        if self.available_from and self.available_to and self.available_from > self.available_to:
            raise ValidationError("available_from must be on or before available_to.")


class Hotel(InventoryItem):
    class BoardBasis(models.TextChoices):
        ROOM_ONLY = "room_only", "Room only"
        BREAKFAST = "breakfast", "Breakfast included"
        HALF_BOARD = "half_board", "Half board"
        FULL_BOARD = "full_board", "Full board"
        ALL_INCLUSIVE = "all_inclusive", "All inclusive"

    city = models.CharField(max_length=120, default="Budapest")
    star_rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} star") for i in range(1, 6)], null=True, blank=True
    )
    room_type = models.CharField(max_length=120, blank=True)
    board_basis = models.CharField(
        max_length=20, choices=BoardBasis.choices, default=BoardBasis.BREAKFAST
    )
    max_occupancy = models.PositiveSmallIntegerField(default=2)

    class Meta(InventoryItem.Meta):
        verbose_name = "Hotel"
        verbose_name_plural = "Hotels"


class Tour(InventoryItem):
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    language = models.CharField(max_length=80, blank=True)
    meeting_point = models.CharField(max_length=200, blank=True)
    min_participants = models.PositiveSmallIntegerField(null=True, blank=True)
    max_participants = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta(InventoryItem.Meta):
        verbose_name = "Tour"
        verbose_name_plural = "Tours"


class Bus(InventoryItem):
    vehicle_type = models.CharField(max_length=120, blank=True)
    seat_capacity = models.PositiveSmallIntegerField(null=True, blank=True)
    route_description = models.CharField(max_length=255, blank=True)
    pickup_location = models.CharField(max_length=200, blank=True)

    class Meta(InventoryItem.Meta):
        verbose_name = "Bus"
        verbose_name_plural = "Buses"


class VendorPackage(InventoryItem):
    """An inseparable, supplier-priced bundle (e.g. room + transfer + tour).

    Unlike a composed package, the price here is set as a whole by the
    supplier and is not attributable to individual layers.
    """

    includes_hotel = models.BooleanField(default=True)
    includes_transfer = models.BooleanField(default=True)
    includes_tour = models.BooleanField(default=False)
    nights = models.PositiveSmallIntegerField(null=True, blank=True)
    inclusions_description = models.TextField(
        help_text="Free-text description of everything bundled into this package."
    )

    class Meta(InventoryItem.Meta):
        verbose_name = "Vendor-native package"
        verbose_name_plural = "Vendor-native packages"


class ComposedPackage(models.Model):
    """A package the agency assembles itself from separate inventory layers.

    Each linked layer keeps its own price (snapshotted at composition time
    so later price changes on the source item don't silently change a
    package already quoted to a customer); the total is their sum.
    """

    name = models.CharField(max_length=200)
    hotel = models.ForeignKey(
        Hotel, on_delete=models.PROTECT, null=True, blank=True, related_name="composed_packages"
    )
    tour = models.ForeignKey(
        Tour, on_delete=models.PROTECT, null=True, blank=True, related_name="composed_packages"
    )
    bus = models.ForeignKey(
        Bus, on_delete=models.PROTECT, null=True, blank=True, related_name="composed_packages"
    )
    hotel_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tour_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bus_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.EUR
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, default=Decimal("0.00")
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Composed package"
        verbose_name_plural = "Composed packages"

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if not any([self.hotel_id, self.tour_id, self.bus_id]):
            raise ValidationError("A composed package needs at least one of hotel, tour or bus.")

    def save(self, *args, **kwargs):
        if self.hotel_id and self.hotel_price is None:
            self.hotel_price = self.hotel.price
        if self.tour_id and self.tour_price is None:
            self.tour_price = self.tour.price
        if self.bus_id and self.bus_price is None:
            self.bus_price = self.bus.price
        self.total_price = sum(
            price for price in (self.hotel_price, self.tour_price, self.bus_price) if price
        ) or Decimal("0.00")
        super().save(*args, **kwargs)
