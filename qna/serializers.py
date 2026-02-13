# qna/serializers.py
from rest_framework import serializers
from .models import Question, Answer

class AnswerSerializer(serializers.ModelSerializer):
    mufti_name = serializers.CharField(source='mufti.get_full_name', read_only=True)
    mufti_email = serializers.EmailField(source='mufti.email', read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'content', 'approval_status', 'mufti_name', 'mufti_email', 'created_at', 'updated_at']
        read_only_fields = ['approval_status', 'mufti_name', 'mufti_email', 'created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'content', 'status', 
            'user_name', 'user_email', 'created_at', 
            'updated_at', 'answer'
        ]
        read_only_fields = ['status', 'user_name', 'user_email', 'created_at', 'updated_at']

    def get_answer(self, obj):
        if hasattr(obj, 'answer'):
            return AnswerSerializer(obj.answer).data
        return None