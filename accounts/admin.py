from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "company",
        "role",
        "is_active",
    )

    list_filter = (
        "company",
        "role",
        "is_active",
    )

    search_fields = (
        "user__username",
        "company__trade_name",
    )
    