from rest_framework import generics
from .models import BlogPost
from .serializers import BlogPostSerializer
from rest_framework import generics, filters
from .models import BlogPost,Comment
from .serializers import BlogPostSerializer,CreateCommentSerializer,CommentSerializer
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view




class BlogPostListAPIView(generics.ListAPIView):
    queryset = BlogPost.objects.filter(status='published').order_by('-created_at')
    serializer_class = BlogPostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']


class CommentListAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        blog_id = self.kwargs['blog_id']
        return Comment.objects.filter(
            blog_post__id=blog_id,
            is_active=True
        ).select_related('user')

class CommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CreateCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        blog_post = generics.get_object_or_404(
            BlogPost, 
            id=self.kwargs['blog_id'],
            status='published'
        )
        serializer.save(
            user=self.request.user,
            blog_post=blog_post
        )

class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CreateCommentSerializer
        return CommentSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user == instance.user or request.user.is_staff:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "You do not have permission to delete this comment."},
            status=status.HTTP_403_FORBIDDEN
        )