from rest_framework import serializers
from .models import BlogPost,Comment


class CommentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'user_email', 'user_name']
        read_only_fields = ['created_at', 'user_email', 'user_name']

class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']
        extra_kwargs = {
            'content': {'required': True}
        }
        
class BlogPostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)  # Add many=True
   
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'created_at', 'updated_at', 'featured_image','comments']


