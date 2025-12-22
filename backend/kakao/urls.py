from django.urls import path
from .views import KakaoRouteAPIView

urlpatterns = [
    path('route/', KakaoRouteAPIView.as_view()),
    path('directions/', KakaoRouteAPIView.as_view(), name='kakao-directions'),
]