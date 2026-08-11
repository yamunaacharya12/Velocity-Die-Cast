from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class Brand(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_featured = models.BooleanField(default=True, help_text="Show in the homepage brand strip")

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop') + f'?category={self.slug}'


class Product(models.Model):
    SCALE_CHOICES = [
        ('1:64', '1:64'),
        ('1:43', '1:43'),
        ('1:24', '1:24'),
        ('1:18', '1:18'),
    ]
    CAR_TYPE_CHOICES = [
        ('super', 'Supercar / Hypercar'),
        ('f1', 'Formula 1'),
        ('classic', 'Classic'),
    ]
    TAG_CHOICES = [
        ('', 'No Tag'),
        ('new', 'New Arrival'),
        ('best', 'Best Seller'),
        ('limited', 'Limited Edition'),
        ('sale', 'On Sale'),
    ]

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    scale = models.CharField(max_length=6, choices=SCALE_CHOICES, default='1:64')
    material = models.CharField(max_length=60, default='Metal Die-Cast')
    color = models.CharField(max_length=80, blank=True)
    dimensions = models.CharField(max_length=80, blank=True, help_text='e.g. 2.9" L x 1.1" W x 0.8" H')
    manufacturer = models.CharField(max_length=80, default='Velocity Die-Cast Co.')
    release_year = models.PositiveIntegerField(default=2024)
    recommended_age = models.PositiveIntegerField(default=6, help_text='Minimum recommended age')

    car_type = models.CharField(max_length=10, choices=CAR_TYPE_CHOICES, default='super',
                                 help_text='Controls the placeholder illustration style when no photo is uploaded')
    accent_color = models.CharField(max_length=7, default='#e4002b',
                                     help_text='Hex color used for the placeholder illustration, e.g. #e4002b')
    has_spoiler = models.BooleanField(default=False)

    description = models.TextField(blank=True)
    features = models.TextField(blank=True, help_text='One feature per line')

    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=25)
    tag = models.CharField(max_length=10, choices=TAG_CHOICES, blank=True)

    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f'{self.brand_id and self.brand.name or ""}-{self.name}')
            slug = base
            i = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f'{base}-{i}'
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.brand.name} {self.name}'

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    @property
    def feature_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def stock_status(self):
        if self.stock <= 0:
            return 'out'
        if self.stock < 10:
            return 'low'
        return 'ok'

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((self.old_price - self.price) / self.old_price * 100)
        return 0

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(agg, 1) if agg else 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def sku(self):
        return f'VDC-{self.pk:04d}' if self.pk else 'VDC-0000'


class ProductImage(models.Model):
    """Extra angle shots for the product gallery."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'Image for {self.product.name}'


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=60, help_text='Display name (auto-filled for logged in users)')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.rating}\u2605 \u2014 {self.product.name} by {self.name}'


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user.username} \u2665 {self.product.name}'
