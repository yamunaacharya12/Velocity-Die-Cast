import random
import string
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone


def generate_order_number():
    return 'VDC-' + ''.join(random.choices(string.digits, k=6))


class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('card', 'Credit / Debit Card'),
        ('paypal', 'PayPal'),
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
        ('fonepay', 'Fonepay'),
        ('cod', 'Cash on Delivery'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False, default=generate_order_number)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='orders')

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)

    address = models.CharField(max_length=200)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=60, default='Nepal')

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cod')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='processing')

    created_at = models.DateTimeField(auto_now_add=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.estimated_delivery:
            self.estimated_delivery = (timezone.now() + timedelta(days=6)).date()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

    @property
    def status_step(self):
        order_steps = ['processing', 'packed', 'shipped', 'delivered']
        return order_steps.index(self.status) if self.status in order_steps else 0


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('product.Product', on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=60, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f'{self.product_name} x{self.quantity}'
