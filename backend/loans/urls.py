from django.urls import path

from .views import LoanProductListView, LoanProductDetailView, LoanRecommendView

urlpatterns = [
    path("", LoanProductListView.as_view()),
    path("recommend/", LoanRecommendView.as_view()),
    path("<str:fin_prdt_cd>/", LoanProductDetailView.as_view()),
]
