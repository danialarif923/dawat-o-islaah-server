from django.urls import path, include
from . import views

urlpatterns = [
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path("get-ayat/", views.get_ayat, name="get-ayat"),
    path("api/quran/", views.get_surah_ayat, name="get-surah-ayat"),
    path("fonts.css", views.custom_fonts_css, name="fonts_css"),
    path("api/fonts/", views.get_custom_fonts, name="get-fonts"),
    path("api/tafseer/", views.get_tafseer, name="get-tafseer"),
]
