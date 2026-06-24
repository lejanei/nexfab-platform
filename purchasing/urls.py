from django.urls import path

from accounts import views

from .views import create_replenishment_order, purchase_order_attachment_delete, purchase_order_delete, purchase_order_list, purchase_order_receiving, receive_material, receiving_stock_workspace, register_purchase, send_for_approval
from .views import purchase_order_detail
from .views import purchase_order_create
from .views import purchase_order_workspace
from .views import purchase_order_item_delete
from .views import purchase_order_item_edit
from .views import purchase_order_attachments
from .views import stock_consumption_workspace



urlpatterns = [
    path(
        "pedidos/",
        purchase_order_list,
        name="purchase_order_list"
    ),

    path(
        "pedidos/<int:pk>/",
        purchase_order_detail,
        name="purchase_order_detail"
    ),
    
    path(
        "pedidos/novo/",
        purchase_order_create,
        name="purchase_order_create"
    ),
    
    path(
        "workspace/<int:pk>/",
        purchase_order_workspace,
        name="purchase_order_workspace"
    ),
    
    path(
        "itens/<int:pk>/excluir/",
        purchase_order_item_delete,
        name="purchase_order_item_delete"
    ),
    
    path(
        "item/<int:pk>/editar/",
        purchase_order_item_edit,
        name="purchase_order_item_edit"
    ),
    
    path(
        "workspace/<int:pk>/attachments/",
        purchase_order_attachments,
        name="purchase_order_attachments"
    ),
    
    path(
        "attachment/<int:pk>/delete/",
        purchase_order_attachment_delete,
        name="purchase_order_attachment_delete"
    ),
    
    path(
        "workflow/<int:pk>/send/",
        send_for_approval,
        name="send_for_approval",
    ),
    
    path(
        "workflow/<int:pk>/purchase/",
        register_purchase,
        name="register_purchase"
    ),

    path(
        "workflow/<int:pk>/receive/",
        receive_material,
        name="receive_material"
    ),  
    
    path(
        "pedidos/<int:pk>/excluir/",
        purchase_order_delete,
        name="purchase_order_delete"
    ),
    
    path(
        "pedidos/<int:pk>/receber/",
        purchase_order_receiving,
        name="purchase_order_receiving"
    ),
    
    path(
        "pedidos/<int:pk>/entrada-estoque/",
        receiving_stock_workspace,
        name="receiving_stock_workspace"
    ),
    
    path(
        "produto/<int:pk>/consumir/",
        stock_consumption_workspace,
        name="stock_consumption_workspace"
    ),
    
    path(
        "reposicao/<int:product_id>/criar-pedido/",
        create_replenishment_order,
        name="create_replenishment_order"
    ),
            
]