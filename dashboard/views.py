from django.shortcuts import render

from purchasing.models import PurchaseOrder


def dashboard(request):

    context = {

        "open_orders":
        PurchaseOrder.objects.filter(
            status="OPEN"
        ).count(),

        "approved_orders":
        PurchaseOrder.objects.filter(
            status="APPROVED"
        ).count(),

        "purchased_orders":
        PurchaseOrder.objects.filter(
            status="PURCHASED"
        ).count(),

        "received_orders":
        PurchaseOrder.objects.filter(
            status="RECEIVED"
        ).count(),

        "last_orders":
        PurchaseOrder.objects.order_by(
            "-created_at"
        )[:10]

    }

    return render(
        request,
        "dashboard/index.html",
        context
    )