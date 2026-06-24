from django import forms


class StockAdjustmentForm(forms.Form):

    MOVEMENT_TYPES = [
        ("IN", "Entrada"),
        ("OUT", "Saída"),
        ("ADJUST", "Ajuste"),
    ]

    movement_type = forms.ChoiceField(
        choices=MOVEMENT_TYPES,
        label="Tipo"
    )

    quantity = forms.DecimalField(
        max_digits=12,
        decimal_places=3,
        label="Quantidade"
    )

    reason = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Motivo"
    )