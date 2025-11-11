from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Customer(models.Model):
    """Customer model for CRM system"""
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:
        ordering = ['-created_at']


class Product(models.Model):
    """Product model for CRM system"""
    name = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

    class Meta:
        ordering = ['name']


class Order(models.Model):
    """Order model for CRM system"""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    products = models.ManyToManyField(Product, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} - ${self.total_amount}"

    def calculate_total(self):
        """Calculate total amount from associated products"""
        total = sum(product.price for product in self.products.all())
        return total

    class Meta:
        ordering = ['-order_date']
