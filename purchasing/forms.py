from django import forms

from .models import PurchaseOrder
from .models import PurchaseOrderItem
from .models import PurchaseOrderAttachment


class PurchaseOrderForm(forms.ModelForm):

    class Meta:

        model = PurchaseOrder

        fields = [

            "supplier",

            "cost_center",

            "priority",

            "description",

        ]
        

class PurchaseOrderItemForm(forms.ModelForm):

    class Meta:
        model = PurchaseOrderItem

        fields = [
            "code",
            "description",
            "quantity",
            "unit",
            "unit_price",
        ]

        widgets = {
            "code": forms.TextInput(
                attrs={
                    "placeholder": "Ex: 6205"
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "placeholder": "Ex: Rolamento SKF 6205"
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "step": "0.001",
                    "min": "0"
                }
            ),
            "unit": forms.TextInput(
                attrs={
                    "placeholder": "UN"
                }
            ),
            "unit_price": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0"
                }
            ),
        }
        
class PurchaseOrderAttachmentForm(forms.ModelForm):

    class Meta:
        model = PurchaseOrderAttachment

        fields = [
            "file",
            "file_type",
        ]

        widgets = {
            "file": forms.FileInput(),
            "file_type": forms.Select(),
        }
        
from django import forms


class StockConsumptionForm(forms.Form):

    quantity = forms.DecimalField(
        max_digits=12,
        decimal_places=3,
        label="Quantidade"
    )

    cost_center = forms.CharField(
        max_length=100,
        label="Centro de custo"
    )

    reason = forms.ChoiceField(
        choices=[
            ("MAINTENANCE", "Manutenção"),
            ("PRODUCTION", "Produção"),
            ("GENERAL", "Consumo geral"),
            ("OTHER", "Outro"),
        ],
        label="Motivo"
    )

    observation = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Observação"
    )
    
class PurchaseOrderHeaderForm(
    forms.ModelForm
):

    class Meta:

        model = PurchaseOrder

        fields = [
            "supplier",
            "cost_center",
            "priority",
            "description",
        ]