from django.urls import path
from .views import (
    ProductSyncView, 
    ProductListView, 
    ProductDetailView, 
    BankListView,
    ProductJoinView,
)

urlpatterns = [
    path('sync/', ProductSyncView.as_view()),
    path("", ProductListView.as_view()),
    path("<int:pk>/", ProductDetailView.as_view()),
    path("banks/", BankListView.as_view()),
    path("<int:pk>/join/", ProductJoinView.as_view()),
]