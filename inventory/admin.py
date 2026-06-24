from django.contrib import admin

from .models import Product
from .models import StockMovement


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "description",
        "unit",
        "current_stock",
        "minimum_stock",
        "location",
        "is_active",
    )

    search_fields = (
        "code",
        "description",
    )

    list_filter = (
        "is_active",
        "unit",
    )
    
@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "movement_type",
        "quantity",
        "previous_stock",
        "new_stock",
        "user",
        "created_at",
    )

    list_filter = (
        "movement_type",
        "created_at",
    )

    search_fields = (
        "product__code",
        "product__description",
        "reason",
    )