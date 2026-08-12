import os
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Agent
from inventory.models import Bus, ComposedPackage, Hotel, Tour, VendorPackage
from sales.models import Quote, Request


class Command(BaseCommand):
    """Idempotent bootstrap for a hosted preview: ensures a superuser exists
    and, if the sales table is still empty, seeds a few sample inventory
    rows and one request with competing quotes so the admin isn't blank.

    Safe to run on every deploy.
    """

    help = "Create the demo superuser and seed sample data if none exists yet."

    def handle(self, *args, **options):
        self._ensure_superuser()
        if Request.objects.exists():
            self.stdout.write("Sample data already present, skipping seed.")
            return
        self._seed_sample_data()
        self.stdout.write(self.style.SUCCESS("Seed complete."))

    def _ensure_superuser(self):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        if not password:
            self.stdout.write("DJANGO_SUPERUSER_PASSWORD not set, skipping superuser creation.")
            return
        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email, "is_staff": True, "is_superuser": True}
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
        else:
            self.stdout.write(f"Superuser '{username}' already exists.")

    def _seed_sample_data(self):
        user, _ = User.objects.get_or_create(
            username="dana_hotels", defaults={"email": "dana@kortosh.example", "first_name": "Dana"}
        )
        agent, _ = Agent.objects.get_or_create(
            user=user,
            defaults={"display_name": "Dana Kovacs", "vendor_category": "hotel", "phone": "+36 20 123 4567"},
        )

        start = date.today() + timedelta(days=30)
        end = start + timedelta(days=10)

        h1 = Hotel.objects.create(
            name="Corinthia Budapest", supplier_name="Corinthia Group", price=120, city="Budapest",
            available_from=start, available_to=end, star_rating=5, room_type="Deluxe Double",
            board_basis="breakfast", quantity_available=8,
            terms="Free cancellation up to 7 days before arrival.",
        )
        h2 = Hotel.objects.create(
            name="Aquincum Hotel", supplier_name="Danubius", price=95, city="Budapest",
            available_from=start, available_to=end, star_rating=4, room_type="Standard Double",
            board_basis="half_board", quantity_available=12,
        )
        h3 = Hotel.objects.create(
            name="Ibis Styles City", supplier_name="Accor", price=70, city="Budapest",
            available_from=start, available_to=end, star_rating=3, room_type="Standard Twin",
            board_basis="room_only", quantity_available=20,
        )
        tour = Tour.objects.create(
            name="Budapest City Tour", supplier_name="City Tours Kft", price=25,
            available_from=start, available_to=end, duration_hours=3, language="Hebrew",
            meeting_point="Deak Ferenc ter",
        )
        bus = Bus.objects.create(
            name="Airport Transfer", supplier_name="Kalotours Bus", price=15,
            available_from=start, available_to=end, vehicle_type="Minibus", seat_capacity=19,
            pickup_location="Budapest Airport T2",
        )
        vp = VendorPackage.objects.create(
            name="Hilton All-in-One 3N", supplier_name="Hilton Group", price=180,
            available_from=start, available_to=end, nights=3, includes_hotel=True,
            includes_transfer=True, includes_tour=True,
            inclusions_description="3 nights room + airport transfer + Danube evening tour",
        )
        cp = ComposedPackage.objects.create(
            name="Composed BUD 3N - Corinthia", hotel=h1, tour=tour, bus=bus,
            notes="Assembled for the Cohen family request.",
        )
        req = Request.objects.create(
            assigned_agent=agent, customer_name="Yossi Cohen", customer_email="yossi@example.com",
            customer_phone="+972 50 123 4567", destination="Budapest", date_from=start,
            date_to=start + timedelta(days=3), num_adults=2, num_children=1, status="in_progress",
            source_channel="Israir", notes="Wants a 5-star hotel if possible.",
        )
        for h in (h1, h2, h3):
            Quote.objects.create(request=req, quote_type="hotel", hotel=h, price=h.price, currency=h.currency)
        Quote.objects.create(
            request=req, quote_type="vendor_package", vendor_package=vp, price=vp.price, currency=vp.currency
        )
        Quote.objects.create(
            request=req, quote_type="composed_package", composed_package=cp,
            price=cp.total_price, currency=cp.currency,
        )
