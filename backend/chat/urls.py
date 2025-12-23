from django.urls import path
from .views import chat, history, reset

urlpatterns = [
    path("", chat),
    path("history/", history),
    path("reset/", reset),
]