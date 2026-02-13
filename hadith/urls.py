from django.urls import path
from .views import get_hadith

urlpatterns = [
    path('get-hadith/', get_hadith, name='get_hadith'),
] 