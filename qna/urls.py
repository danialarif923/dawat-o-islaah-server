from django.urls import path
from .views import UserQuestionListCreateAPI, UserQuestionDetailAPI

urlpatterns = [
    path('', UserQuestionListCreateAPI.as_view(), name='user-questions'),
    path('<int:pk>/', UserQuestionDetailAPI.as_view(), name='user-question-detail'),
]