from django.urls import path
from .views import recommend_product

urlpatterns = [
    path("", recommend_product),
]