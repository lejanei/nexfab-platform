from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path(
        "",
        include("dashboard.urls")
    ),

    path(
        "compras/",
        include("purchasing.urls")
    ),

    path(
        "admin/",
        admin.site.urls
    ),
    
    path(
        "estoque/",
        include("inventory.urls")
    ),
    
    path(
    "login/",
    auth_views.LoginView.as_view(
        template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )