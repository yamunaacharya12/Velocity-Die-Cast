from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from product.models import Brand, Category, Product, Review
from orders.models import Order, OrderItem
from pages.models import BlogPost


CATEGORIES = [
    'Supercar / Hypercar',
    'Sports Car',
    'Formula 1 Cars',
    'Classic Cars',
    'Muscle Cars',
    'JDM Cars',
    'Luxury Cars',
    'Rally Cars',
    'GT / Racing Cars',
    'Le Mans / Endurance',
    'SUV / Off-Road',
    'Electric Cars',
    'Limited Edition',
    'Concept Cars',
]


BRANDS = [
    'Lamborghini',
    'Nissan',
    'Toyota',
    'Ferrari',
    'Bugatti',
    'Porsche',
    'McLaren',
    'Koenigsegg',
    'BMW',
    'Mercedes-Benz',
    'Audi',
    'Chevrolet',
    'Dodge',
    'Rolls-Royce'
]

PRODUCTS = [
    dict(name="Aventador SVJ", brand="Lamborghini", category="Supercar / Hypercar", car_type="super",
         accent="#e4002b", scale="1:64", price=12.99, old_price=None, rating_seed=4.8,
         color="Verde Alceo Green / Racing Red", year=2024, dims='2.9" L x 1.1" W x 0.8" H', age=6,
         tag="best", stock=38, spoiler=False,
         desc="The Aventador SVJ die-cast replica captures every aggressive line of Sant'Agata's track-honed flagship, from the ALA active aero to the quad exhaust tips, cast in solid zinc alloy and finished in deep pearlescent red.",
         features=["Die-cast metal body & chassis", "Rolling rubber-tread wheels", "Opening doors detail sculpt", "Authentic livery decals"]),
    dict(name="GT-R R35 Nismo", brand="Nissan", category="JDM Cars", car_type="super",
         accent="#0057d9", scale="1:64", price=11.49, old_price=None, rating_seed=4.7,
         color="Pearl White / Nismo Blue", year=2025, dims='2.9" L x 1.1" W x 0.7" H', age=6,
         tag="new", stock=52, spoiler=False,
         desc="Godzilla returns in miniature — the R35 Nismo edition features the iconic wide-body kit, carbon-fiber accented spoiler sculpt, and Nismo blue racing stripe over pearl white base coat.",
         features=["Die-cast metal body & chassis", "Detailed brake caliper paint", "Wide-body fender sculpt", "Collector number plate"]),
    dict(name="Supra MK5", brand="Toyota", category="JDM Cars", car_type="super",
         accent="#ffc629", scale="1:64", price=10.99, old_price=13.99, rating_seed=4.6,
         color="Renaissance Orange / Black", year=2024, dims='2.8" L x 1.0" W x 0.7" H', age=6,
         tag="sale", stock=64, spoiler=False,
         desc="A tribute to the fifth-generation drift icon — dual-tone orange over gloss black with a race-spec ducktail spoiler and deep-dish alloy wheel sculpt.",
         features=["Die-cast metal body & chassis", "Ducktail spoiler detail", "Deep-dish wheel design", "Matte-black hood accent"]),
    dict(name="SF90 Stradale", brand="Ferrari", category="Supercar / Hypercar", car_type="super",
         accent="#e4002b", scale="1:64", price=14.99, old_price=None, rating_seed=4.9,
         color="Rosso Corsa Red", year=2024, dims='2.9" L x 1.1" W x 0.8" H', age=8,
         tag="limited", stock=21, spoiler=False,
         desc="Maranello's plug-in hybrid hypercar rendered in classic Rosso Corsa, with the signature side air intakes and rear light bar sculpted in fine relief.",
         features=["Die-cast metal body & chassis", "Sculpted side air intakes", "Rear light-bar detailing", "Collector series packaging"]),
    dict(name="Chiron Super Sport", brand="Bugatti", category="Supercar / Hypercar", car_type="super",
         accent="#0057d9", scale="1:43", price=34.99, old_price=None, rating_seed=4.9,
         color="French Blue / Carbon Black", year=2024, dims='4.1" L x 1.6" W x 1.1" H', age=8,
         tag="limited", stock=14, spoiler=True,
         desc="A larger-format 1:43 tribute to the fastest production Bugatti — French Racing Blue over exposed carbon weave, with the signature horseshoe grille and C-line body crease faithfully reproduced.",
         features=["Premium 1:43 large-format scale", "Exposed carbon-weave engine cover", "Horseshoe grille detail", "Individually numbered base"]),
    dict(name="911 GT3 RS", brand="Porsche", category="Sports Car", car_type="super",
         accent="#f4f5f6", scale="1:64", price=11.99, old_price=None, rating_seed=4.8,
         color="Chalk White / Acid Green", year=2025, dims='2.7" L x 1.0" W x 0.7" H', age=6,
         tag="new", stock=47, spoiler=True,
         desc="The track-focused 911 GT3 RS with its towering swan-neck rear wing and functional-look front canards, finished in Chalk White with Acid Green accent striping.",
         features=["Die-cast metal body & chassis", "Swan-neck wing sculpt", "Front canard detailing", "Center-lock wheel design"]),
    dict(name="720S", brand="McLaren", category="Supercar / Hypercar", car_type="super",
         accent="#ffc629", scale="1:64", price=12.49, old_price=None, rating_seed=4.7,
         color="Papaya Orange", year=2023, dims='2.9" L x 1.1" W x 0.7" H', age=6,
         tag="best", stock=33, spoiler=False,
         desc="McLaren's dihedral-door supercar in signature Papaya Orange, with the distinctive eye-socket headlamp sculpt and double-skin aero panels captured in fine die-cast detail.",
         features=["Die-cast metal body & chassis", "Dihedral door line sculpt", "Eye-socket headlamp detail", "Racing heritage livery option"]),
    dict(name="Jesko Absolut", brand="Koenigsegg", category="Supercar / Hypercar", car_type="super",
         accent="#888c96", scale="1:18", price=249.99, old_price=299.99, rating_seed=5.0,
         color="Titanium Silver", year=2024, dims='9.8" L x 4.1" W x 2.6" H', age=14,
         tag="limited", stock=6, spoiler=True,
         desc="Our flagship 1:18 masterwork — hand-finished titanium silver paintwork, functioning steering, opening dihedral doors, hood and engine bay, and a fully detailed triplex-suspension chassis.",
         features=["Museum-grade 1:18 scale", "Opening doors, hood & engine bay", "Functional steering mechanism", "Individually numbered, display case included"]),
    dict(name="M4 Competition", brand="BMW", category="Sports Car", car_type="super",
         accent="#0057d9", scale="1:64", price=9.99, old_price=None, rating_seed=4.5,
         color="Isle of Man Green / Kidney Grille Black", year=2023, dims='2.8" L x 1.0" W x 0.7" H', age=6,
         tag="", stock=71, spoiler=False,
         desc="The M4 Competition's signature vertical kidney grille and M-quad exhaust are sculpted in fine relief over a deep Isle of Man Green base coat.",
         features=["Die-cast metal body & chassis", "Signature kidney grille sculpt", "Quad exhaust detail", "M-stripe livery accents"]),
    dict(name="AMG GT Black Series", brand="Mercedes-Benz", category="Sports Car", car_type="super",
         accent="#24252e", scale="1:64", price=11.99, old_price=None, rating_seed=4.7,
         color="Obsidian Black", year=2023, dims='2.9" L x 1.0" W x 0.7" H', age=6,
         tag="", stock=29, spoiler=True,
         desc="AMG's most track-focused GT wears deep obsidian black with a towering adjustable rear wing and vented carbon hood sculpt.",
         features=["Die-cast metal body & chassis", "Adjustable rear wing sculpt", "Vented hood detail", "AMG badge decals"]),
    dict(name="R8 V10 Performance", brand="Audi", category="Sports Car", car_type="super",
         accent="#888c96", scale="1:64", price=10.49, old_price=12.99, rating_seed=4.6,
         color="Kemora Grey", year=2023, dims='2.8" L x 1.0" W x 0.7" H', age=6,
         tag="sale", stock=58, spoiler=False,
         desc="Audi's mid-engine icon in Kemora Grey with the signature singleframe grille and LED light-blade sculpt reproduced in crisp detail.",
         features=["Die-cast metal body & chassis", "Singleframe grille sculpt", "LED light-blade detailing", "Side blade color accent"]),
    dict(name="Championship Racer '24", brand="Ferrari", category="Formula 1 Cars", car_type="f1",
         accent="#e4002b", scale="1:43", price=27.99, old_price=None, rating_seed=4.8,
         color="Scarlet Red / Carbon Black", year=2024, dims='4.3" L x 1.9" W x 1.0" H', age=8,
         tag="new", stock=24, spoiler=False,
         desc="A faithful 1:43 reproduction of the season's championship-winning open-wheel racer, with front and rear wing assemblies, halo device, and full sponsor livery.",
         features=["Detailed halo device sculpt", "Multi-element front & rear wings", "Full season livery decals", "Display stand included"]),
    dict(name="'67 Camaro SS", brand="Chevrolet", category="Classic Cars", car_type="classic",
         accent="#ffc629", scale="1:64", price=9.49, old_price=None, rating_seed=4.7,
         color="Butternut Yellow / Black Stripes", year=1967, dims='2.9" L x 1.0" W x 0.8" H', age=6,
         tag="best", stock=66, spoiler=False,
         desc="A muscle-car legend cast true to form, with dual black racing stripes over Butternut Yellow, chrome bumpers, and whitewall-style tires.",
         features=["Die-cast metal body & chassis", "Chrome bumper detailing", "Period-correct whitewall tires", "Racing stripe livery"]),
    dict(name="'70 Charger R/T", brand="Dodge", category="Classic Cars", car_type="classic",
         accent="#e4002b", scale="1:64", price=9.49, old_price=11.99, rating_seed=4.6,
         color="Hemi Orange", year=1970, dims='2.9" L x 1.0" W x 0.8" H', age=6,
         tag="sale", stock=40, spoiler=False,
         desc="The quintessential muscle coupe in Hemi Orange, with hidden headlamp sculpt, dual scoop hood, and chrome R/T badging.",
         features=["Die-cast metal body & chassis", "Hidden headlamp sculpt", "Dual-scoop hood detail", "Chrome R/T badge decal"]),
    dict(name="Countach Gold Chrome", brand="Lamborghini", category="Limited Edition", car_type="super",
         accent="#ffc629", scale="1:64", price=24.99, old_price=None, rating_seed=4.9,
         color="Full Gold Chrome", year=1988, dims='2.9" L x 1.1" W x 0.8" H', age=8,
         tag="limited", stock=9, spoiler=False,
         desc="A wedge-era icon dipped entirely in gold chrome plating for our Treasure Hunt collector series — individually bagged and numbered.",
         features=["Full gold chrome plating", "Individually numbered card", "Scissor-door sculpt detail", "Collector-grade packaging"]),
    dict(name="Divo Diamond Edition", brand="Bugatti", category="Limited Edition", car_type="super",
         accent="#0057d9", scale="1:18", price=349.99, old_price=None, rating_seed=5.0,
         color="Diamond Black / French Blue", year=2024, dims='9.6" L x 3.9" W x 2.5" H', age=14,
         tag="limited", stock=4, spoiler=True,
         desc="Our rarest release — the track-tuned Divo finished in diamond-flake black with French Blue accents, housed in a museum display case with a solid metal nameplate.",
         features=["Museum-grade 1:18 scale", "Diamond-flake paint finish", "Opening doors & engine bay", "Solid metal nameplate & case"]),
]

SAMPLE_REVIEWS = [
    ("Marcus T.", 5, "The detail on this thing is unreal in hand — paint depth and panel gaps put it above anything I've bought at retail."),
    ("Priya S.", 5, "Arrived in mint packaging with zero paint chips. Shipping to Kathmandu took just 6 days."),
    ("Daniel K.", 4, "Gorgeous detail, wheels roll smooth. Only wish the box insert was a bit sturdier for long-term storage."),
    ("J. Whitfield", 5, "Paint quality exceeded my expectations at this price point — panel gaps are consistent and wheels roll true."),
    ("R. Bhattarai", 5, "Fast shipping, perfect packaging. Now the centerpiece of my display shelf."),
    ("C. Nwosu", 4, "Great detail overall, though I wish the mirrors were slightly more defined. Still a solid addition."),
]

BLOG_POSTS = [
    dict(title="Inside the Jesko Absolut: Six Months From Scan to Shelf", accent="#888c96",
         excerpt="A behind-the-scenes look at how our flagship 1:18 hypercar went from CAD file to collector's case.",
         content="Every Velocity flagship release starts the same way: a full 3D scan of the source vehicle, often taken directly at a manufacturer preview event.\nFrom there, our tooling team spends up to six months refining panel lines, badge placement, and proportions across as many as six physical prototype revisions.\nThe Jesko Absolut was our most ambitious build yet, with a functioning steering rack and opening dihedral doors that required an entirely new hinge assembly."),
    dict(title="Collector Spotlight: A 400-Piece Shelf Built Over 12 Years", accent="#e4002b",
         excerpt="We sat down with longtime collector R. Bhattarai to talk about what it takes to build a serious collection.",
         content="R. Bhattarai's shelf started with a single 1:64 Lamborghini bought at a mall kiosk in 2014.\nToday it spans four display cases and over 400 models, organized by manufacturer era rather than brand.\nHis advice for new collectors: buy what you love first, and worry about 'investment value' never — the joy is in the shelf, not the resale."),
    dict(title="1:64 vs 1:18 — Choosing Your Collecting Scale", accent="#0057d9",
         excerpt="Pocket scale or museum scale? Here's how to decide which fits your space, budget, and collecting style.",
         content="1:64 scale is the entry point for most collectors — affordable, easy to display in volume, and available across nearly every brand we carry.\n1:18 scale, by contrast, is built for detail: opening doors, functioning steering, and engine bays you can actually inspect.\nMost serious collectors end up doing both — a large 1:64 wall display, and a handful of 1:18 pieces reserved for cars that mean the most to them."),
]


class Command(BaseCommand):
    help = "Seed the Velocity Die-Cast store with brands, categories, products, reviews, blog posts, and demo accounts."

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories...")
        cat_objs = {}
        for name in CATEGORIES:
            cat_objs[name], _ = Category.objects.get_or_create(name=name)

        self.stdout.write("Seeding brands...")
        brand_objs = {}
        for name in BRANDS:
            brand_objs[name], _ = Brand.objects.get_or_create(name=name)

        self.stdout.write("Seeding products...")
        created_products = []
        for p in PRODUCTS:
            product, created = Product.objects.update_or_create(
                name=p['name'], brand=brand_objs[p['brand']],
                defaults=dict(
                    category=cat_objs[p['category']],
                    car_type=p['car_type'],
                    accent_color=p['accent'],
                    has_spoiler=p['spoiler'],
                    scale=p['scale'],
                    price=p['price'],
                    old_price=p['old_price'],
                    color=p['color'],
                    release_year=p['year'],
                    dimensions=p['dims'],
                    recommended_age=p['age'],
                    tag=p['tag'],
                    stock=p['stock'],
                    description=p['desc'],
                    features="\n".join(p['features']),
                    is_active=True,
                )
            )
            created_products.append(product)

        self.stdout.write("Seeding reviews...")
        for product in created_products:
            if product.reviews.exists():
                continue
            import random
            for name, rating, text in random.sample(SAMPLE_REVIEWS, k=min(3, len(SAMPLE_REVIEWS))):
                Review.objects.create(product=product, name=name, rating=rating, comment=text)

        self.stdout.write("Seeding blog posts...")
        for bp in BLOG_POSTS:
            BlogPost.objects.get_or_create(
                title=bp['title'],
                defaults=dict(excerpt=bp['excerpt'], content=bp['content'], accent_color=bp['accent']),
            )

        self.stdout.write("Creating demo accounts...")
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@velocitydiecast.com', 'admin12345')
            self.stdout.write(self.style.SUCCESS("  Superuser created: admin / admin12345"))
        else:
            self.stdout.write("  Superuser 'admin' already exists.")

        demo_user, created = User.objects.get_or_create(
            username='demo@velocitydiecast.com',
            defaults=dict(email='demo@velocitydiecast.com', first_name='Alex', last_name='Rivera'),
        )
        if created:
            demo_user.set_password('demo12345')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS("  Demo customer created: demo@velocitydiecast.com / demo12345"))

        if not Order.objects.filter(user=demo_user).exists() and created_products:
            order = Order.objects.create(
                user=demo_user, full_name="Alex Rivera", email=demo_user.email, phone="+977 9812345678",
                address="House 12, Baneshwor Marg", city="Kathmandu", state="Bagmati", zip_code="44600",
                country="Nepal", subtotal=34.98, shipping_cost=9.99, tax=2.80, total=47.77,
                payment_method="esewa", status="delivered",
            )
            for product in created_products[:2]:
                OrderItem.objects.create(
                    order=order, product=product, product_name=product.name,
                    brand_name=product.brand.name, unit_price=product.price, quantity=1,
                )
            order2 = Order.objects.create(
                user=demo_user, full_name="Alex Rivera", email=demo_user.email, phone="+977 9812345678",
                address="House 12, Baneshwor Marg", city="Kathmandu", state="Bagmati", zip_code="44600",
                country="Nepal", subtotal=249.99, shipping_cost=0, tax=20.00, total=269.99,
                payment_method="cod", status="shipped",
            )
            OrderItem.objects.create(
                order=order2, product=created_products[7], product_name=created_products[7].name,
                brand_name=created_products[7].brand.name, unit_price=created_products[7].price, quantity=1,
            )
            self.stdout.write(self.style.SUCCESS("  Sample orders created for demo account."))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {Product.objects.count()} products, {Category.objects.count()} categories, "
            f"{Brand.objects.count()} brands, {Review.objects.count()} reviews, {BlogPost.objects.count()} blog posts."
        ))