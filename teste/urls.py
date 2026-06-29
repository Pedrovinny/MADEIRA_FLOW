from django.contrib import admin
from django.urls import path
from core import views  # ← mudar de teste.views para core.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
]