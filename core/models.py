from django.db import models


class Company(models.Model):
    name = models.CharField("Razão Social", max_length=200)
    trade_name = models.CharField("Nome Fantasia", max_length=200)

    cnpj = models.CharField(
        "CNPJ",
        max_length=18,
        unique=True
    )

    email = models.EmailField(
        "E-mail",
        blank=True,
        null=True
    )

    phone = models.CharField(
        "Telefone",
        max_length=20,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        "Ativo",
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["trade_name"]

    def __str__(self):
        return self.trade_name