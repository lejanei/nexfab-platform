import os

from django.db import models
from django.contrib.auth.models import User
from core.models import Company
from django.db.models import Max
from django.db import transaction
from django.db.models import Sum


class Supplier(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=200
    )

    cnpj = models.CharField(
        max_length=18,
        blank=True,
        null=True
    )

    contact_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    notes = models.TextField(
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

    def __str__(self):
        return self.name

class CostCenter(models.Model):

    TYPE_CHOICES = [
        ("OPEX", "OPEX"),
        ("CAPEX", "CAPEX"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    code = models.CharField(
        max_length=20
    )

    name = models.CharField(
        max_length=100
    )

    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
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

    def __str__(self):
        return f"{self.code} - {self.name}"
    
class PurchaseOrder(models.Model):        
    def save(self, *args, **kwargs):

        from django.utils import timezone

        current_user = getattr(self, "_current_user", None)

        is_new = self.pk is None

        old_status = None

        if self.pk:
            old_status = (
                PurchaseOrder.objects
                .filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )

        if not self.number:

            last_order = PurchaseOrder.objects.order_by("-id").first()

            next_id = 1

            if last_order:
                next_id = last_order.id + 1

            self.number = f"PC-{next_id:06d}"

        super().save(*args, **kwargs)

        if is_new:

            PurchaseOrderLog.objects.create(
                purchase_order=self,
                user=current_user,
                action="CREATED",
                message=f"Pedido {self.number} criado."
            )

        if old_status and old_status != self.status:

            if self.status == "APPROVED":
                self.approved_at = timezone.now()

            elif self.status == "PURCHASED":
                self.purchased_at = timezone.now()

            elif self.status == "RECEIVED":
                self.received_at = timezone.now()

            elif self.status == "CANCELLED":
                self.cancelled_at = timezone.now()

            PurchaseOrder.objects.filter(
                pk=self.pk
            ).update(
                approved_at=self.approved_at,
                purchased_at=self.purchased_at,
                received_at=self.received_at,
                cancelled_at=self.cancelled_at,
            )

            messages = {
                "APPROVED": "Pedido aprovado.",
                "PURCHASED": "Compra realizada.",
                "RECEIVED": "Material recebido.",
                "CANCELLED": "Pedido cancelado.",
            }

            PurchaseOrderLog.objects.create(
                purchase_order=self,
                user=current_user,
                action=self.status,
                message=messages[self.status]
            )
    @property
    def calculated_total(self):

        return (

            self.items.aggregate(

                Sum(
                    "total_price"
                )

            )[
                "total_price__sum"
            ]

            or 0

        )
            
            
    STATUS_CHOICES = [
        ("DRAFT", "Rascunho"),
        ("OPEN", "Em Aprovação"),
        ("APPROVED", "Aprovado"),
        ("PURCHASED", "Comprado"),
        ("RECEIVED", "Recebido"),
        ("CANCELLED", "Cancelado"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Baixa"),
        ("NORMAL", "Normal"),
        ("HIGH", "Alta"),
        ("URGENT", "Urgente"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    number = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    requester = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT
    )

    cost_center = models.ForeignKey(
        CostCenter,
        on_delete=models.PROTECT
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="NORMAL"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )

    purchased_at = models.DateTimeField(
        blank=True,
        null=True
    )

    received_at = models.DateTimeField(
        blank=True,
        null=True
    )

    cancelled_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.number
    
class PurchaseOrderItem(models.Model):

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    code = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    description = models.CharField(
        max_length=255
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    unit = models.CharField(
        max_length=20,
        default="UN"
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def save(self, *args, **kwargs):

        self.total_price = (
            self.quantity *
            self.unit_price
        )

        super().save(*args, **kwargs)

        total = (
            self.purchase_order.items
            .aggregate(
                Sum("total_price")
            )
            ["total_price__sum"]
            or 0
        )

        PurchaseOrder.objects.filter(
            pk=self.purchase_order.pk
        ).update(
            total_amount=total
        )

    def __str__(self):
        return self.description
    
class PurchaseOrderLog(models.Model):

    ACTION_CHOICES = [
        ("CREATED", "Criado"),
        ("UPDATED", "Atualizado"),
        ("APPROVED", "Aprovado"),
        ("PURCHASED", "Comprado"),
        ("RECEIVED", "Recebido"),
        ("CANCELLED", "Cancelado"),
        ("COMMENT", "Comentário"),
        ("ATTACHMENT", "Anexo"),
    ]

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.purchase_order.number} - {self.action}"
    
class PurchaseOrderAttachment(models.Model):
    
    @property
    def filename(self):
        return os.path.basename(
            self.file.name
        )
    

    FILE_TYPE_CHOICES = [
        ("QUOTE", "Orçamento"),
        ("INVOICE", "Nota Fiscal"),
        ("IMAGE", "Imagem"),
        ("OTHER", "Outro"),
    ]

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(
        upload_to="purchase_orders/attachments/"
    )

    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default="QUOTE"
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.purchase_order.number} - {self.file_type}"

