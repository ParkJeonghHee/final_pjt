from django.urls import path
from .views import ProductSyncView

urlpatterns = [
    path('sync/', ProductSyncView.as_view()),
]