from django.urls import path
from .views import MasailListAPIView

urlpatterns = [
    path('', MasailListAPIView.as_view(), name='masail-list-api'),
]