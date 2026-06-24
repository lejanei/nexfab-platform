from django.urls import include, path
from .views import inventory_list, product_workspace

from . import views

urlpatterns=[

    path(

        "",
        inventory_list,
        name="inventory_list"
    ),
    
    path(
        "produto/<int:pk>/",
        product_workspace,
        name="product_workspace"
    ),
    
    path(
        "produto/<int:pk>/ajustar/",
        views.stock_adjustment_workspace,
        name="stock_adjustment_workspace"
    ),
    
]