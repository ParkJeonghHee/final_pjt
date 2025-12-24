from django.urls import path

from .views import MarketSummaryView, MarketHistoryView

urlpatterns = [
    path("summary/", MarketSummaryView.as_view()),
    path("history/", MarketHistoryView.as_view()),
]
