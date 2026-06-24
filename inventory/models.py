from django.db import models

from core.models import Company


class Product(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    code = models.CharField(
        max_length=50
    )

    description = models.CharField(
        max_length=255
    )

    unit = models.CharField(
        max_length=20,
        default="UN"
    )

    current_stock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0
    )

    minimum_stock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0
    )

    location = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def stock_status(self):

        if self.current_stock <= 0:
            return "CRITICAL"

        if self.current_stock < self.minimum_stock:
            return "LOW"

        return "NORMAL"

    def __str__(self):
        return f"{self.code} - {self.description}"
    
from django.contrib.auth.models import User


class StockMovement(models.Model):

    MOVEMENT_TYPES = [
        ("IN", "Entrada"),
        ("OUT", "Saída"),
        ("ADJUST", "Ajuste"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="movements"
    )

    movement_type = models.CharField(
        max_length=10,
        choices=MOVEMENT_TYPES
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    previous_stock = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    new_stock = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    reason = models.TextField(
        blank=True,
        null=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.code} - {self.movement_type} - {self.quantity}"