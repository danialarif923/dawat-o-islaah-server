from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('user_management.urls')),
    path('api/blogs/', include('blog.urls')),
    path('api/books/', include('books.urls')),
    path('api/masails/', include('masails.urls')),
    path('api/questions/', include('qna.urls')),
    path('api/hadith/', include('hadith.urls')),
    path("qna/", include("qna.urls")),
    path('quran/', include('quran.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Dawat O Islaah Admin"
admin.site.site_title = "Dawat O Islaah Admin Portal"
admin.site.index_title = "Welcome to Dawat O Islaah Portal"
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)