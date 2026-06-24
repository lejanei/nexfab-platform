from django.contrib import admin
from .models import Supplier
from .models import CostCenter
from .models import PurchaseOrder
from .models import PurchaseOrderItem
from .models import PurchaseOrderLog
from .models import PurchaseOrderAttachment

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    
class PurchaseOrderLogInline(admin.TabularInline):
    model = PurchaseOrderLog

    extra = 0

    readonly_fields = (
        "user",
        "action",
        "message",
        "created_at",
    )

    can_delete = False
    max_num = 0
    
    def has_add_permission(self, request, obj=None):
        return False

class PurchaseOrderAttachmentInline(admin.TabularInline):
    model = PurchaseOrderAttachment
    extra = 0
    readonly_fields = (
        "uploaded_by",
        "created_at",
    )
    
@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj._current_user = request.user
        super().save_model(request, obj, form, change)
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        order = form.instance

        total = sum(
            item.total_price
            for item in order.items.all()
        )

        order.total_amount = total
        order.save()  
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, PurchaseOrderAttachment):
                if not instance.uploaded_by:
                    instance.uploaded_by = request.user

            instance.save()

        formset.save_m2m()
    

    readonly_fields = (
    "number",
    "total_amount",
    "created_at",
    "approved_at",
    "purchased_at",
    "received_at",
    "cancelled_at",
    )   
    
    list_display = (
    "number",
    "supplier",
    "cost_center",
    "status",
    "priority",
    "total_amount",
    "created_at",
    )

    list_filter = (
        "status",
        "priority",
    )

    search_fields = (
        "number",
    )

    inlines = [
        PurchaseOrderItemInline,
        PurchaseOrderLogInline,
        PurchaseOrderAttachmentInline,
    ]

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "cnpj",
        "email",
        "is_active",
    )

    search_fields = (
        "name",
        "cnpj",
    )

    list_filter = (
        "is_active",
    )


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "type",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
    )

    list_filter = (
        "type",
        "is_active",
    )