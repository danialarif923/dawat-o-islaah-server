# qna/views.py
from rest_framework import generics, permissions
from .models import Question
from .serializers import QuestionSerializer

class UserQuestionListCreateAPI(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter().prefetch_related('answer')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserQuestionDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(user=self.request.user).prefetch_related('answer')