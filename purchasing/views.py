from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Sum
from django.db.models import F
from rest_framework import request
from .forms import PurchaseOrderForm, PurchaseOrderHeaderForm
from .models import PurchaseOrder, PurchaseOrderAttachment
from .forms import PurchaseOrderItemForm
from .models import PurchaseOrderItem
from .forms import PurchaseOrderAttachmentForm
from .models import PurchaseOrderLog
from inventory.models import Product
from inventory.models import StockMovement
from .forms import StockConsumptionForm
from .models import CostCenter
from. models import Supplier
from core.utils import get_company

def purchase_order_list(request):
    
    company = get_company(request)
    orders = PurchaseOrder.objects.filter(
        company=company
    ).order_by(
        "-created_at"
    )
    
    critical_products = Product.objects.filter(
    company=company,
    is_active=True,
    current_stock__lt=F("minimum_stock")
    ).order_by(
        "description"
    )

    for product in critical_products:
        product.suggested_purchase = (
            product.minimum_stock - product.current_stock
        )

    context = {
        "orders": orders,
        
        "critical_products": critical_products,
        
        "critical_products_count": critical_products.count(),
        
        "total_orders": PurchaseOrder.objects.filter(
            company=company
        ).count(),

        "draft_count": PurchaseOrder.objects.filter(
            company=company,
            status="DRAFT"
        ).count(),

        "approved_count": PurchaseOrder.objects.filter(
            company=company,
            status="APPROVED"
        ).count(),

        "purchased_count": PurchaseOrder.objects.filter(
            company=company,
            status="PURCHASED"
        ).count(),

        "received_count": PurchaseOrder.objects.filter(
            company=company,
            status="RECEIVED"
        ).count(),

        "total_value": sum(
            order.calculated_total for order in orders
        ),
    }

    return render(
        request,
        "purchasing/purchase_order_list.html",
        context
    )

def purchase_order_detail(request, pk):

    company = get_company(request)

    order = get_object_or_404(
        PurchaseOrder,
        pk=pk,
        company=company
    )

    return render(
        request,
        "purchasing/purchase_order_detail.html",
        {
            "order": order
        }
    )
    
def purchase_order_create(request):

    if request.method == "POST":

        form = PurchaseOrderForm(
            request.POST
        )

        if form.is_valid():

            order = form.save(
                commit=False
            )

            profile = request.user.userprofile

            order.company = profile.company

            order.requester = request.user

            order.save()

        return redirect(
            "purchase_order_workspace",
            pk=order.pk
        )

    else:

        form = PurchaseOrderForm()

    return render(

        request,

        "purchasing/purchase_order_create.html",

        {

            "form": form

        }

    )
    
def purchase_order_workspace(request, pk):

    company = get_company(request)

    order = get_object_or_404(
        PurchaseOrder,
        pk=pk,
        company=company
    )
    
    if request.method == "POST":

        header_form = PurchaseOrderHeaderForm(
            request.POST,
            instance=order
        )

        if header_form.is_valid():

            header_form.save()

            PurchaseOrderLog.objects.create(
                purchase_order=order,
                user=request.user,
                action="UPDATED",
                message="Dados do pedido atualizados."
            )

            return redirect(
                "purchase_order_workspace",
                pk=order.pk
            )

    else:
        header_form = PurchaseOrderHeaderForm(
            instance=order
        )

    if request.method == "POST":

        item_form = PurchaseOrderItemForm(
            request.POST
        )

        if item_form.is_valid():

            item = item_form.save(
                commit=False
            )

            item.purchase_order = order
            item.save()

            return redirect(
                "purchase_order_workspace",
                pk=order.pk
            )

    else:

        item_form = PurchaseOrderItemForm()
        
        header_form = PurchaseOrderHeaderForm(
            instance=order
        )

    return render(
        request,
        "purchasing/workspace.html",
        {
            "order": order,
            "item_form": item_form,
            "header_form": header_form,
        }
    )
    
def purchase_order_item_delete(request,pk):

    item = get_object_or_404(
        PurchaseOrderItem,
        pk=pk
    )

    order_id = item.purchase_order.pk

    item.delete()

    total = (
    PurchaseOrderItem.objects
    .filter(
        purchase_order_id=order_id
    )
    .aggregate(
        Sum(
            "total_price"
        )
    )[
        "total_price__sum"
    ]
    or 0
    )

    PurchaseOrder.objects.filter(
        pk=order_id
    ).update(
        total_amount=total
    )
    
            
    return redirect(
        "purchase_order_workspace",
        pk=order_id
        )

def purchase_order_item_edit(request, pk):

    item = get_object_or_404(
        PurchaseOrderItem,
        pk=pk
    )

    order = item.purchase_order

    if request.method == "POST":

        item_form = PurchaseOrderItemForm(
            request.POST,
            instance=item
        )

        if item_form.is_valid():

            item_form.save()

            return redirect(
                "purchase_order_workspace",
                pk=order.pk
            )

    else:

        item_form = PurchaseOrderItemForm(
            instance=item
        )

    return render(
        request,
        "purchasing/item_edit.html",
        {
            "order": order,
            "item": item,
            "item_form": item_form,
        }

    )

def purchase_order_attachments(request, pk):

    company = get_company(request)

    order = get_object_or_404(
        PurchaseOrder,
        pk=pk,
        company=company
    )

    if request.method == "POST":

        form = PurchaseOrderAttachmentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            attachment = form.save(
                commit=False
            )

            attachment.purchase_order = order
            attachment.uploaded_by = request.user
            attachment.save()

            return redirect(
                "purchase_order_attachments",
                pk=order.pk
            )

    else:

        form = PurchaseOrderAttachmentForm()

    attachments = order.attachments.all()

    return render(
        request,
        "purchasing/attachments.html",
        {
            "order": order,
            "attachments": attachments,
            "form": form,
        }
    )
    
def purchase_order_attachment_delete(
    request,
    pk
    ):

    attachment = get_object_or_404(
        PurchaseOrderAttachment,
        pk=pk
    )

    order_pk = attachment.purchase_order.pk

    attachment.delete()

    return redirect(
        "purchase_order_attachments",
        pk=order_pk
    )
    
def send_for_approval(request, pk):

    company = get_company(request)

    order = get_object_or_404(
        PurchaseOrder,
        pk=pk,
        company=company
    )

    if order.status == "DRAFT":

        order.status = "APPROVED"
        order._current_user = request.user
        order.save()

    return redirect(
        "purchase_order_workspace",
        pk=order.pk
    )
    
def register_purchase(request, pk):

    company = get_company(request)

    order = get_object_or_404(
        PurchaseOrder,
        pk=pk,
        company=company
    )

    if order.status == "APPROVED":

        order.status = "PURCHASED"
        order._current_user = request.user
        order.save()

    return redirect(
        "purchase_order_workspace",
        pk=order.pk
    )

def receive_material(request, pk):

    company = get_company(request)

    order = get_object_or_404(
        PurchaseOrder,
        pk=pk,
        company=company
    )
    

    if order.status == "PURCHASED":

        order.status = "RECEIVED"
        order._current_user = request.user
        order.save()

    return redirect(
        "purchase_order_workspace",
        pk=order.pk
    )
    
def purchase_order_delete(request, pk):

    company = get_company(request)

    order = get_object_or_404(
        PurchaseOrder,
        pk=pk,
        company=company
    )

    if order.status == "DRAFT":

        order.delete()

        messages.success(
            request,
            "Pedido excluído com sucesso."
        )

    else:

        messages.error(
            request,
            "Somente pedidos em rascunho podem ser excluídos."
        )

    return redirect(
        "purchase_order_list"
    )
    
def purchase_order_receiving(request, pk):

    company = get_company(request)

    order = get_object_or_404(
        PurchaseOrder,
        pk=pk,
        company=company
    )

    if request.method == "POST":

        notes = request.POST.get(
            "notes",
            ""
        ).strip()

        if not notes:
            notes = "Material recebido."

        if order.status == "PURCHASED":
            order.status = "RECEIVED"
            order._current_user = request.user
            order.save()

            PurchaseOrderLog.objects.create(
                purchase_order=order,
                user=request.user,
                action="RECEIVED",
                message=notes
            )

            messages.success(
                request,
                "Recebimento finalizado com sucesso."
            )

        else:

            messages.error(
                request,
                "Este pedido não está disponível para recebimento."
            )

        return redirect(
            "purchase_order_workspace",
            pk=order.pk
        )

    return render(
        request,
        "purchasing/receiving_workspace.html",
        {
            "order": order
        }
    )
    
def receiving_stock_workspace(request, pk):

    company = get_company(request)

    order = get_object_or_404(
        PurchaseOrder,
        pk=pk,
        company=company
    )

    products = Product.objects.filter(
        is_active=True
    ).order_by(
        "description"
    )

    if request.method == "POST":

        movements_created = 0

        for item in order.items.all():

            product_id = request.POST.get(
                f"product_{item.pk}"
            )

            if not product_id:
                continue

            product = get_object_or_404(
                Product,
                pk=product_id
            )

            previous_stock = product.current_stock

            new_stock = previous_stock + item.quantity

            product.current_stock = new_stock
            product.save()

            StockMovement.objects.create(
                product=product,
                movement_type="IN",
                quantity=item.quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                reason=f"Entrada automática pelo pedido {order.number}",
                user=request.user
            )

            movements_created += 1

        if movements_created > 0:

            order.status = "RECEIVED"
            order._current_user = request.user
            order.save()

            PurchaseOrderLog.objects.create(
                purchase_order=order,
                user=request.user,
                action="RECEIVED",
                message=f"Entrada em estoque realizada. {movements_created} item(ns) movimentado(s)."
            )

            messages.success(
                request,
                "Entrada em estoque realizada com sucesso."
            )

            return redirect(
                "purchase_order_workspace",
                pk=order.pk
            )

        messages.error(
            request,
            "Selecione pelo menos um produto de estoque."
        )

    return render(
        request,
        "purchasing/receiving_stock_workspace.html",
        {
            "order": order,
            "products": products,
        }
    )

def stock_consumption_workspace(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if request.method == "POST":

        form = StockConsumptionForm(
            request.POST
        )

        if form.is_valid():

            quantity = form.cleaned_data["quantity"]
            cost_center = form.cleaned_data["cost_center"]
            reason = form.cleaned_data["reason"]
            observation = form.cleaned_data["observation"]

            previous_stock = product.current_stock

            if quantity > previous_stock:

                messages.error(
                    request,
                    "Quantidade maior que o saldo disponível."
                )

                return redirect(
                    "stock_consumption_workspace",
                    pk=product.pk
                )

            new_stock = previous_stock - quantity

            product.current_stock = new_stock
            product.save()

            StockMovement.objects.create(
                product=product,
                movement_type="OUT",
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                reason=f"Consumo - {reason} | CC: {cost_center} | {observation}",
                user=request.user
            )

            messages.success(
                request,
                "Consumo registrado com sucesso."
            )

            return redirect(
                "product_workspace",
                pk=product.pk
            )

    else:

        form = StockConsumptionForm()

    return render(
        request,
        "inventory/stock_consumption_workspace.html",
        {
            "product": product,
            "form": form,
        }
    )
    
def create_replenishment_order(request, product_id):

    product = get_object_or_404(
        Product,
        pk=product_id
    )

    suggested_quantity = (
        product.minimum_stock - product.current_stock
    )

    if suggested_quantity <= 0:

        messages.error(
            request,
            "Este produto não está abaixo do estoque mínimo."
        )

        return redirect(
            "purchase_order_list"
        )

    profile = request.user.userprofile
    
    cost_center = CostCenter.objects.filter(
        company=profile.company
    ).first()
    
    # MELHORAR FUTURAMENTE PARA PERMITIR SELEÇÃO DE CENTRO DE CUSTO OU CRIAÇÃO DE CENTRO DE CUSTO ESPECÍFICO PARA REPOSIÇÃO
    if not cost_center:

        messages.error(
            request,
            "Cadastre um centro de custo antes de criar pedidos por reposição."
        )

        return redirect(
            "purchase_order_list"
        )
    # FORNECEDOR PADRÃO PARA REPOSIÇÃO - MELHORAR FUTURAMENTE PARA PERMITIR SELEÇÃO DE FORNECEDOR OU CRIAÇÃO DE FORNECEDOR ESPECÍFICO PARA REPOSIÇÃO
    supplier = Supplier.objects.filter(
        company=profile.company
    ).first()

    if not supplier:

        messages.error(
            request,
            "Cadastre um fornecedor antes de criar pedidos por reposição."
        )

        return redirect(
            "purchase_order_list"
        )
    order = PurchaseOrder.objects.create(
        company=profile.company,
        requester=request.user,
        cost_center=cost_center,
        supplier=supplier,
        status="DRAFT",
        priority="NORMAL",
        description=(
            f"Pedido gerado pela reposição automática do estoque. "
            f"Produto: {product.code} - {product.description}. "
            f"Saldo atual: {product.current_stock}. "
            f"Estoque mínimo: {product.minimum_stock}."
        )
    )

    item = PurchaseOrderItem.objects.create(
        purchase_order=order,
        code=product.code,
        description=product.description,
        quantity=suggested_quantity,
        unit=product.unit,
        unit_price=0
    )

    PurchaseOrderLog.objects.create(
        purchase_order=order,
        user=request.user,
        action="CREATED",
        message=(
            f"Pedido criado pela reposição inteligente. "
            f"Produto {product.code}. "
            f"Quantidade sugerida: {suggested_quantity}."
        )
    )

    messages.success(
        request,
        "Pedido de reposição criado com sucesso."
    )

    return redirect(
        "purchase_order_workspace",
        pk=order.pk
    )
