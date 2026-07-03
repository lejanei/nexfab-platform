from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from core.models import Company
from accounts.models import UserProfile
from purchasing.models import Supplier, CostCenter
from inventory.models import Product


class Command(BaseCommand):
    help = "Cria dados de demonstração da Nexfab"

    def handle(self, *args, **kwargs):

        self.stdout.write("Criando ambiente demo Nexfab...")

        company, created = Company.objects.get_or_create(
            name="NexFab Demo"
        )

        self.stdout.write(f"Empresa: {company.name}")

        admin_user, created = User.objects.get_or_create(
            username="demo"
        )

        if created:
            admin_user.set_password("demo123")
            admin_user.email = "demo@nexfab.com.br"
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

        UserProfile.objects.get_or_create(
            user=admin_user,
            company=company
        )

        cost_centers = [
            ("ADM001", "Administrativo"),
            ("MAN001", "Manutenção"),
            ("PROD001", "Produção"),
            ("ENG001", "Engenharia"),
            ("ALM001", "Almoxarifado"),
        ]

        for code, name in cost_centers:
            CostCenter.objects.get_or_create(
                company=company,
                code=code,
                defaults={
                    "name": name
                }
            )

        suppliers = [
            "WEG",
            "SKF",
            "Schneider",
            "Sick",
            "SEW",
            "Fornecedor Padrão",
        ]

        for name in suppliers:
            Supplier.objects.get_or_create(
                company=company,
                name=name
            )

        products = [
            ("ROL-6205", "Rolamento SKF 6205", "UN", 10, 5, "A1"),
            ("ROL-6206", "Rolamento SKF 6206", "UN", 2, 5, "A1"),
            ("COR-B57", "Correia em V B57", "UN", 3, 5, "B2"),
            ("COR-B58", "Correia em V B58", "UN", 8, 5, "B2"),
            ("MOT-2CV", "Motor WEG 2CV", "UN", 0, 1, "M1"),
            ("MOT-5CV", "Motor WEG 5CV", "UN", 1, 1, "M1"),
            ("INV-GD20", "Inversor INVT GD20", "UN", 1, 2, "E1"),
            ("CONT-18A", "Contator 18A", "UN", 6, 3, "E2"),
            ("CONT-32A", "Contator 32A", "UN", 1, 3, "E2"),
            ("SEN-IND", "Sensor Indutivo", "UN", 8, 4, "E3"),
            ("BOT-VERDE", "Botão Verde NA", "UN", 12, 5, "E4"),
            ("BOT-VERM", "Botão Vermelho NF", "UN", 4, 5, "E4"),
            ("CABO-PP-4X25", "Cabo PP 4x2,5mm", "M", 35, 20, "C1"),
            ("FUS-10A", "Fusível 10A", "UN", 20, 10, "E5"),
            ("FUS-20A", "Fusível 20A", "UN", 4, 10, "E5"),
            ("OLEO-68", "Óleo Hidráulico 68", "L", 50, 20, "Q1"),
            ("GRAXA-EP2", "Graxa EP2", "KG", 6, 10, "Q2"),
        ]

        for code, description, unit, current_stock, minimum_stock, location in products:
            Product.objects.get_or_create(
                company=company,
                code=code,
                defaults={
                    "description": description,
                    "unit": unit,
                    "current_stock": current_stock,
                    "minimum_stock": minimum_stock,
                    "location": location,
                    "is_active": True,
                }
            )

        self.stdout.write(
            self.style.SUCCESS("Ambiente demo criado com sucesso.")
        )