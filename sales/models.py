import uuid

from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import Agent
from inventory.models import Bus, ComposedPackage, Currency, Hotel, Tour, VendorPackage


class Request(models.Model):
    """A sales request pulled from the shared inbox and assigned to an agent.

    Customer contact fields and the source channel are captured now even
    though phase 1 has no lead-management or duplicate-detection logic yet,
    so phase 3 can be built on top of this table without adding columns
    that change existing behaviour.
    """

    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In progress"
        QUOTED = "quoted", "Quoted"
        CLOSED_WON = "closed_won", "Closed - won"
        CLOSED_LOST = "closed_lost", "Closed - lost"

    reference_code = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    assigned_agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    customer_name = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=50, blank=True)
    source_channel = models.CharField(
        max_length=100,
        default="shared_inbox",
        help_text="Where the request came in from, e.g. shared_inbox, Israir, Kavei Chofesha.",
    )

    destination = models.CharField(max_length=120, default="Budapest")
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    num_adults = models.PositiveSmallIntegerField(default=1)
    num_children = models.PositiveSmallIntegerField(default=0)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference_code} - {self.customer_name or 'Unnamed'}"

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Quote(models.Model):
    """One vendor's offer against a request.

    A request can hold several quotes (e.g. three competing hotel offers,
    or a vendor package alongside a composed package) so the team can
    compare them before a winner is picked. `is_selected` is reserved for
    that future step; phase 1 does not act on it.
    """

    class QuoteType(models.TextChoices):
        HOTEL = "hotel", "Hotel"
        TOUR = "tour", "Tour"
        BUS = "bus", "Bus"
        VENDOR_PACKAGE = "vendor_package", "Vendor-native package"
        COMPOSED_PACKAGE = "composed_package", "Composed package"

    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="quotes")
    quote_type = models.CharField(max_length=20, choices=QuoteType.choices)

    hotel = models.ForeignKey(
        Hotel, on_delete=models.PROTECT, null=True, blank=True, related_name="quotes"
    )
    tour = models.ForeignKey(
        Tour, on_delete=models.PROTECT, null=True, blank=True, related_name="quotes"
    )
    bus = models.ForeignKey(
        Bus, on_delete=models.PROTECT, null=True, blank=True, related_name="quotes"
    )
    vendor_package = models.ForeignKey(
        VendorPackage, on_delete=models.PROTECT, null=True, blank=True, related_name="quotes"
    )
    composed_package = models.ForeignKey(
        ComposedPackage, on_delete=models.PROTECT, null=True, blank=True, related_name="quotes"
    )

    price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Quoted price, snapshotted at quote time."
    )
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.EUR)
    valid_until = models.DateField(null=True, blank=True)
    is_selected = models.BooleanField(
        default=False,
        help_text="Reserved for a future 'pick the winning quote' step. Not used in phase 1.",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Quote #{self.pk} for {self.request.reference_code}"

    _TYPE_FIELD_MAP = {
        QuoteType.HOTEL: "hotel",
        QuoteType.TOUR: "tour",
        QuoteType.BUS: "bus",
        QuoteType.VENDOR_PACKAGE: "vendor_package",
        QuoteType.COMPOSED_PACKAGE: "composed_package",
    }

    def clean(self):
        super().clean()
        linked_fields = ["hotel", "tour", "bus", "vendor_package", "composed_package"]
        linked_values = [getattr(self, f"{field}_id") for field in linked_fields]
        set_count = sum(1 for value in linked_values if value)
        if set_count != 1:
            raise ValidationError(
                "A quote must link to exactly one of: hotel, tour, bus, "
                "vendor_package or composed_package."
            )
        expected_field = self._TYPE_FIELD_MAP.get(self.quote_type)
        if expected_field and not getattr(self, f"{expected_field}_id"):
            raise ValidationError(
                f"quote_type '{self.quote_type}' requires the '{expected_field}' field to be set."
            )
