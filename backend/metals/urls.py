from django.urls import path
from .views import MetalSeriesAPIView

urlpatterns = [
    path("series/", MetalSeriesAPIView.as_view()),
]