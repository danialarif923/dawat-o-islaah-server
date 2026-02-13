from django.urls import path
from .views import (BlogPostListAPIView,CommentListAPIView,
    CommentCreateAPIView,
    CommentDetailAPIView)

urlpatterns = [
    path('', BlogPostListAPIView.as_view(), name='blog-list-api'),
    path('<int:blog_id>/comments/',
         CommentListAPIView.as_view(), name='comment-list'),
    
    # Create comment for a blog
    path('<int:blog_id>/comments/create/',
         CommentCreateAPIView.as_view(), name='comment-create'),
    
    # Comment detail operations
    path('comments/<int:pk>/',
         CommentDetailAPIView.as_view(), name='comment-detail'),
]    