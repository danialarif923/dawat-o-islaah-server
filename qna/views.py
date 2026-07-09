from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q, F

from .models import Question, Category, Bookmark, Answer
from .serializers import QuestionSerializer, CategorySerializer, AnswerSerializer

class CategoryListAPI(generics.ListAPIView):
    """Public endpoint to get all categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class PublicQuestionListAPI(generics.ListAPIView):
    """Public endpoint - returns approved questions with optional filtering."""
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Question.objects.filter(status='approved').filter(
            Q(answer__isnull=True) | Q(answer__approval_status='approved')
        ).select_related('user', 'answer', 'answer__mufti', 'category')

        # Filter by category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        # Filter by saved (requires auth)
        saved_only = self.request.query_params.get('saved')
        if saved_only == 'true' and self.request.user.is_authenticated:
            qs = qs.filter(bookmarked_by__user=self.request.user)

        return qs

    def get_serializer_context(self):
        # Pass request to serializer to determine 'is_saved' status
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ToggleBookmarkAPI(APIView):
    """Toggle save status for a question."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        bookmark, created = Bookmark.objects.get_or_create(user=request.user, question=question)
        if not created:
            bookmark.delete()
            return Response({"is_saved": False, "message": "Removed from saved."})
        return Response({"is_saved": True, "message": "Saved successfully."})

class UserQuestionCreateAPI(generics.CreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserQuestionListAPI(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(user=self.request.user).select_related('user', 'answer', 'answer__mufti')

class UserQuestionDetailAPI(generics.RetrieveAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(user=self.request.user).select_related('user', 'answer', 'answer__mufti')

class IncrementViewAPI(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, pk):
        updated = Question.objects.filter(pk=pk).update(
            view_count=F('view_count') + 1
        )

        if not updated:
            return Response({"error": "Not found"}, status=404)

        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        return Response({"view_count": question.view_count})

class IncrementDownloadAPI(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, pk):
        updated = Question.objects.filter(pk=pk).update(
            download_count=F('download_count') + 1
        )

        if not updated:
            return Response({"error": "Not found"}, status=404)

        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        return Response({"download_count": question.download_count})

class CreateAnswerAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Only admin and mufti roles can answer
        if request.user.role not in ('admin', 'mufti'):
            return Response({"error": "Only muftis and admins can answer questions"}, status=403)

        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

        content = request.data.get("content")
        if not content:
            return Response({"error": "Content is required"}, status=400)

        answer = Answer.objects.create(
            question=question,
            mufti=request.user,
            content=content,
            approval_status='pending'
        )

        return Response(AnswerSerializer(answer).data, status=201)
