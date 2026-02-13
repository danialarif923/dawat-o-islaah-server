from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'description', 'pdf_file', 'cover_image', 'uploaded_at', 'updated_at', 'is_public']