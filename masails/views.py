from rest_framework import generics, filters
from .models import Masail
from .serializers import MasailSerializer


class MasailListAPIView(generics.ListAPIView):
    queryset = Masail.objects.filter(status='published').order_by('-created_at')
    serializer_class = MasailSerializer
    filter_backends = [filters.SearchFilter]  # Add SearchFilter
    search_fields = ['title', 'content']  # Fields to search