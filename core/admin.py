from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "trade_name",
        "cnpj",
        "email",
        "is_active",
    )

    search_fields = (
        "trade_name",
        "cnpj",
    )

    list_filter = (
        "is_active",
    )
    