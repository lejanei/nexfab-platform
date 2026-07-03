from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from core.utils import get_company

from .models import Product, StockMovement
from .forms import StockAdjustmentForm


def inventory_list(request):

    company = get_company(request)

    products = Product.objects.filter(
        company=company,
        is_active=True
    ).order_by(
        "description"
    )

    context = {
        "products": products,
        "total_products": products.count(),

        "normal_products": sum(
            1 for p in products
            if p.stock_status == "NORMAL"
        ),

        "low_products": sum(
            1 for p in products
            if p.stock_status == "LOW"
        ),

        "critical_products": sum(
            1 for p in products
            if p.stock_status == "CRITICAL"
        ),
    }

    return render(
        request,
        "inventory/inventory_list.html",
        context
    )


def product_workspace(request, pk):

    company = get_company(request)

    product = get_object_or_404(
        Product,
        pk=pk,
        company=company
    )

    movements = product.movements.all()

    return render(
        request,
        "inventory/product_workspace.html",
        {
            "product": product,
            "movements": movements,
        }
    )


def stock_adjustment_workspace(request, pk):

    company = get_company(request)

    product = get_object_or_404(
        Product,
        pk=pk,
        company=company
    )

    if request.method == "POST":

        form = StockAdjustmentForm(
            request.POST
        )

        if form.is_valid():

            movement_type = form.cleaned_data["movement_type"]
            quantity = form.cleaned_data["quantity"]
            reason = form.cleaned_data["reason"]

            previous_stock = product.current_stock

            if movement_type == "IN":
                new_stock = previous_stock + quantity

            elif movement_type == "OUT":
                new_stock = previous_stock - quantity

            else:
                new_stock = quantity

            product.current_stock = new_stock
            product.save()

            StockMovement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                reason=reason,
                user=request.user
            )

            messages.success(
                request,
                "Estoque ajustado com sucesso."
            )

            return redirect(
                "product_workspace",
                pk=product.pk
            )

    else:

        form = StockAdjustmentForm()

    return render(
        request,
        "inventory/stock_adjustment_workspace.html",
        {
            "product": product,
            "form": form,
        }
    )