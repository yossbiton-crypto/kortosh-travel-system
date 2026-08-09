from django.conf import settings
from django.db import models


class Agent(models.Model):
    """A staff member who works requests out of the shared inbox.

    Each agent typically owns one vendor category (e.g. hotels), but the
    field is free text/choice rather than an FK so new categories don't
    require a migration.
    """

    class VendorCategory(models.TextChoices):
        HOTEL = "hotel", "Hotels"
        TOUR = "tour", "Tours"
        BUS = "bus", "Buses"
        VENDOR_PACKAGE = "vendor_package", "Vendor packages"
        GENERAL = "general", "General / multiple categories"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agent_profile",
    )
    display_name = models.CharField(max_length=150)
    vendor_category = models.CharField(
        max_length=20,
        choices=VendorCategory.choices,
        default=VendorCategory.GENERAL,
        help_text="The vendor category this agent primarily handles.",
    )
    phone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name
