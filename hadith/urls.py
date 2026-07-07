from django.urls import path
from . import views
from .views import fetch_hadith_from_api, get_hadith, get_had_chapters, get_books, search_hadith

urlpatterns = [

    path("get-books/", get_books, name="get_books"),
    path(
        "fetch-hadith/",
        fetch_hadith_from_api,
        name="fetch_hadith"
    ),

    path(
        "get-hadith/",
        get_hadith,
        name="get_hadith"
    ),
    path("get-chapters/", get_had_chapters, name="get_had_chapters"),
    path('api/get-chapters/', views.get_chapters_by_book, name='get_chapters_by_book'),
    path('search-hadith/', search_hadith, name='search_hadith'),
    
]
