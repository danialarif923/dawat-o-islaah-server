from rest_framework import serializers
from .models import Masail,Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']


        
class MasailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    image = serializers.SerializerMethodField()  # Added field

    class Meta:
        model = Masail
        fields = ['id', 'title', 'slug', 'content', 'category', 'image', 'status', 'created_at', 'updated_at']

    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None