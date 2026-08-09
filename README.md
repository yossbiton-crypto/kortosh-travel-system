# Kortosh Travel System

Inventory and packaging system for a Budapest-based tour operator working
with Israir and Kavei Chofesha. This is **phase 1**: inventory, packaging,
requests/quotes, and a CRUD admin. See "Future phases" below for what's
intentionally deferred.

## Stack

Django 5 + the built-in Django admin as the CRUD interface. SQLite by
default for local development; swap `DATABASES` in `config/settings.py`
for Postgres in production.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open `/admin/`.

## Apps and data model

- **accounts** — `Agent`: a staff member (linked to a Django `User`) who
  owns a vendor category (hotels, tours, buses, vendor packages, or
  general) and gets assigned to requests.

- **inventory** — the bookable inventory:
  - `Hotel`, `Tour`, `Bus`: each has its own price, currency, availability
    window, quantity, and basic terms (shared via an abstract
    `InventoryItem` base). These are separate tables, not a single
    polymorphic "item" table, so each keeps its own domain-specific fields
    (star rating/board basis, duration/language, vehicle type/capacity).
  - `VendorPackage`: an inseparable, supplier-priced bundle (e.g. a hotel
    group selling room + transfer + tour as one price). Not decomposed
    into hotel/tour/bus rows — the supplier sets one price for the whole
    thing.
  - `ComposedPackage`: the agency's own bundle, built by linking a Hotel,
    Tour and/or Bus (at least one required). Each layer's price is
    snapshotted onto the package at composition time (so a later price
    change on the source inventory item doesn't retroactively change a
    package already quoted to a customer), and `total_price` is
    calculated as their sum on save.

- **sales** — requests and quotes:
  - `Request`: one row per inbound sales request. Tracks the assigned
    `Agent`, status, destination/dates/pax, and customer contact info
    (name/email/phone) plus `source_channel`. The contact fields aren't
    used for anything yet, but they're what phase 3's duplicate-request
    detection will match on, so they're captured from day one.
  - `Quote`: one vendor's offer against a `Request`. Links to exactly one
    of `Hotel` / `Tour` / `Bus` / `VendorPackage` / `ComposedPackage`
    (enforced in `clean()`), with its own price/currency snapshot. A
    `Request` can hold many `Quote`s — e.g. three competing hotel offers
    plus a vendor package — with no "winner" logic yet. `Quote.is_selected`
    exists as a placeholder field for that future step but nothing reads
    it in phase 1.

## Admin

All models are registered in Django admin with list filters, search, and
autocomplete pickers for foreign keys. `Request` shows its `Quote`s inline
so an agent can see every quote gathered for a request on one page.

## Future phases (not built, schema only)

- **Phase 2** — generate a quote document (PDF/Word) from a
  `ComposedPackage` or a chosen `Quote`. `Quote` and `ComposedPackage`
  already carry the frozen price data a document generator would need.
- **Phase 3** — lead management and duplicate-request detection across
  agents, using the customer contact fields already on `Request`.
- **Phase 4** — merge everything into one full system. No specific schema
  hooks needed beyond the above; this is an integration phase.
