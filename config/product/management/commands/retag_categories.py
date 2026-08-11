from django.core.management.base import BaseCommand
from product.models import Product, Category, Brand


CATEGORIES = [
    'Supercar / Hypercar', 'Sports Car', 'Formula 1 Cars', 'Classic Cars', 'Muscle Cars',
    'JDM Cars', 'Luxury Cars', 'Rally Cars', 'GT / Racing Cars', 'Le Mans / Endurance',
    'SUV / Off-Road', 'Electric Cars', 'Limited Edition', 'Concept Cars',
]

BRANDS = [
    'Audi', 'BMW', 'Bugatti', 'Chevrolet', 'Dodge', 'Ferrari', 'Koenigsegg',
    'Lamborghini', 'McLaren', 'Mercedes-Benz', 'Nissan', 'Porsche', 'Toyota',
]

# product name -> (new brand name or None to leave brand unchanged, new category name)
RETAG_MAP = {
    "Aventador SVJ": (None, "Supercar / Hypercar"),
    "GT-R R35 Nismo": (None, "JDM Cars"),
    "Supra MK5": (None, "JDM Cars"),
    "SF90 Stradale": (None, "Supercar / Hypercar"),
    "Chiron Super Sport": (None, "Supercar / Hypercar"),
    "911 GT3 RS": (None, "GT / Racing Cars"),
    "720S": (None, "Supercar / Hypercar"),
    "Jesko Absolut": (None, "Supercar / Hypercar"),
    "M4 Competition": (None, "Sports Car"),
    "AMG GT Black Series": (None, "GT / Racing Cars"),
    "R8 V10 Performance": (None, "Sports Car"),
    "Championship Racer '24": ("Ferrari", "Formula 1 Cars"),
    "'67 Camaro SS": (None, "Muscle Cars"),
    "'70 Charger R/T": (None, "Muscle Cars"),
    "Countach Gold Chrome": (None, "Limited Edition"),
    "Divo Diamond Edition": (None, "Limited Edition"),
}


class Command(BaseCommand):
    help = (
        "Fixes existing products so Category reflects a real car segment "
        "instead of duplicating the Brand name. Safe to run on a live database — "
        "only touches brand/category; never touches images, price, stock, or any "
        "product you added yourself that isn't in the known list."
    )

    def handle(self, *args, **options):
        self.stdout.write("Ensuring the correct Brand list exists...")
        for name in BRANDS:
            Brand.objects.get_or_create(name=name)

        self.stdout.write("Ensuring the correct Category list exists...")
        cat_objs = {}
        for name in CATEGORIES:
            cat_objs[name], _ = Category.objects.get_or_create(name=name)

        self.stdout.write("Retagging known products...")
        updated = 0
        missing = []
        for name, (brand_name, category_name) in RETAG_MAP.items():
            product = Product.objects.filter(name=name).first()
            if not product:
                missing.append(name)
                continue
            product.category = cat_objs[category_name]
            if brand_name:
                product.brand, _ = Brand.objects.get_or_create(name=brand_name)
            product.save(update_fields=['category', 'brand'])
            updated += 1
            self.stdout.write(f"  {name} -> category: {category_name}" + (f", brand: {brand_name}" if brand_name else ""))

        if missing:
            self.stdout.write(self.style.WARNING(
                f"\nSkipped (not found in your database): {', '.join(missing)}"
            ))

        stale = list(Category.objects.exclude(name__in=CATEGORIES))
        stale_unused = [c for c in stale if c.products.count() == 0]
        stale_still_used = [c for c in stale if c.products.count() > 0]

        for c in stale_unused:
            self.stdout.write(f"  Removing unused old category: {c.name}")
            c.delete()

        if stale_still_used:
            self.stdout.write(self.style.WARNING(
                "\nThese old categories still have products attached (likely ones you "
                "added yourself) and were left alone — reassign them manually in the admin:"
            ))
            for c in stale_still_used:
                self.stdout.write(f"  {c.name} ({c.products.count()} product(s))")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {updated} product(s) retagged, {len(stale_unused)} unused old "
            f"categor{'y' if len(stale_unused) == 1 else 'ies'} removed."
        ))