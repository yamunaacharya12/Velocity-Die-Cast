# Velocity Die-Cast — Hot Wheels eCommerce Store (Django)

A full, working eCommerce site for premium die-cast collector cars, built on Django. This
replaces the previous generic storefront with a dark, premium "Hot Wheels" theme, a real
product catalog, session-based cart, full checkout → order → confirmation flow, accounts,
wishlist, order tracking, and a set of content pages — all backed by real database models
and the Django admin.

## 1. What's inside

```
config/                    <- Django project root (this is what you run manage.py from)
├── manage.py
├── requirements.txt
├── db.sqlite3              <- pre-seeded with categories, brands, 16 products, reviews,
│                               3 blog posts, an admin account, and a demo customer w/ orders
├── config/                 <- project settings, root urls.py
├── product/                <- Brand, Category, Product, ProductImage, Review, Wishlist
│                               + home/shop/product-detail views + seed_store command
├── cart/                   <- session-based cart (add/update/remove/view)
├── orders/                 <- Order, OrderItem models + checkout/confirmation/tracking
├── accounts/                <- Profile model + login/register/logout/dashboard
├── pages/                  <- ContactMessage, BlogPost models + FAQ/shipping/returns/etc.
├── templates/website/       <- every page template (dark Hot Wheels theme)
├── static/style.css        <- the full theme stylesheet
└── media/                  <- uploaded product photos land here (optional — see below)
```

## 2. Running it locally

```bash
cd config
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Open **http://127.0.0.1:8000/** — the store is already fully seeded, so you don't need to
create any data before your presentation.

If you ever want to reset and reseed:
```bash
del db.sqlite3          # or: rm db.sqlite3
python manage.py migrate
python manage.py seed_store
```
`seed_store` is idempotent — running it again just updates existing records rather than
duplicating them.

## 3. Demo accounts (already created)

| Role            | Username / Email                | Password     |
|-----------------|----------------------------------|--------------|
| Admin (staff)   | `admin`                          | `admin12345` |
| Demo customer   | `demo@velocitydiecast.com`       | `demo12345`  |

The demo customer already has two past orders (one delivered, one shipped) so **My Account
→ Order History** and **Track Order** aren't empty when you demo them. Sign in at `/login/`,
manage the catalog at `/admin/`.

## 4. Product photos

Every product ships with an on-brand placeholder illustration (an inline SVG car, colored
to match that model's `accent_color` field) so the site looks complete with zero setup.
To use real photos instead: open **Admin → Products → (a product)** and upload an image to
the `image` field — the template automatically prefers the real photo over the placeholder
the moment one exists. You can also add extra angle shots per product via the inline
"Product images" section on the same admin page.

## 5. How the core flows work

- **Catalog** (`product` app): `Product` has scale, material, color, dimensions,
  manufacturer, release year, recommended age, price/old_price, stock, and a tag
  (New / Bestseller / Limited / Sale). `Category` and `Brand` are separate models so the
  homepage category grid and brand strip are fully data-driven — add a new brand or
  category from the admin and it shows up automatically.
- **Shop / filtering** (`/shop/`): category, brand, scale, price range, in-stock-only,
  search, and sort are all handled server-side via GET params in `product/views.py::shop`,
  with real pagination.
- **Cart** (`cart` app): stored in the session (`request.session['cart']`), so it persists
  per-visitor without requiring login. Add/update/remove all round-trip through the DB to
  recompute totals, free-shipping threshold, and tax live.
- **Checkout → Order** (`orders` app): submitting the checkout form creates a real `Order`
  + `OrderItem` rows, decrements product stock, clears the cart, and redirects to a
  confirmation page with a generated order number and delivery estimate. Six payment
  methods are selectable (Card, PayPal, eSewa, Khalti, Fonepay, COD); COD is fully "real"
  end-to-end, and the others create the order the same way (no live payment gateway is
  wired in — see note below).
- **Accounts** (`accounts` app): simple email+password auth on top of Django's built-in
  `User` model, plus a `Profile` for shipping details. Dashboard, Order History, and Track
  Order are all `@login_required` (tracking also works for guests by order number).
- **Wishlist**: heart icon on every product card / detail page, toggled via POST, listed at
  `/wishlist/` (requires login).
- **Reviews**: logged-in users can post a star rating + comment on any product detail page;
  `Product.average_rating` / `review_count` are computed live from the `Review` table.
- **Content pages**: About, Contact (saves to `ContactMessage`, visible in admin), Help,
  FAQ (accordion), Shipping, Returns, Privacy, Terms, and a small Blog (`BlogPost` model).

## 6. Payments — what's real vs. simulated

For a class project, wiring six live payment gateways (Stripe, PayPal, eSewa, Khalti,
Fonepay) would need real merchant sandbox accounts you likely don't have yet. What's built
instead is a realistic **checkout that creates a genuine order regardless of the method
chosen** — which is what most graders actually want to see (the data model, the flow, the
confirmation). If you do get Stripe test keys before your presentation, the card fields in
`templates/website/checkout.html` are already laid out for it — say the word and I'll wire
in `stripe.checkout.Session` for the `card` option specifically.

## 7. Presentation tips

- Walk through: Home → Shop (apply a filter) → Product Detail (switch tabs, add a review)
  → Cart → Checkout (pick a payment method) → Confirmation → Account → Order History →
  Track Order. That's the full grading rubric in one pass.
- Show the **Django admin** (`/admin/`) briefly — add a product live, or edit stock, and
  refresh the shop page to show it's a real database, not static content.
- If asked "is this responsive" — resize the browser or open dev tools' device toolbar;
  the whole theme is built on Bootstrap's grid plus custom breakpoints.

## 8. Known limitations (be upfront about these if asked)

- No real payment gateway is charged — this is standard for a student/demo project.
- Product photography is a generated placeholder unless you upload real images via admin.
- `DEBUG = True` and a hardcoded `SECRET_KEY` are fine for local demoing but should not be
  used if you ever deploy this publicly.
