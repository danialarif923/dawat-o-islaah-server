from rest_framework import serializers
from .models import Question, Answer, Category, Bookmark

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    mufti_name = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            'id', 'content', 'approval_status',
            'mufti_name', 'updated_by', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_mufti_name(self, obj):
        full = obj.mufti.get_full_name()
        return full if full.strip() else obj.mufti.email

    def get_updated_by(self, obj):
        return obj.updated_by

class QuestionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        allow_null=True,
        required=False
    )
    is_saved = serializers.SerializerMethodField()
    saves_count = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'content', 'status',
            'category', 'category_id',
            'user_name', 'created_at', 'updated_at',
            'answer', 'is_saved', 'updated_by',
            'view_count', 'download_count', 'saves_count', 'is_most_read'
        ]
        read_only_fields = [
            'id', 'status', 'user_name', 'created_at', 'updated_at', 'answer', 'is_saved', 'saves_count', 'updated_by'
        ]

    def get_user_name(self, obj):
        full = obj.user.get_full_name()
        return full if full.strip() else "Anonymous"

    def get_answer(self, obj):
        from django.core.exceptions import ObjectDoesNotExist
        try:
            answer = obj.answer
        except ObjectDoesNotExist:
            return None
        return AnswerSerializer(answer).data

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
          return Bookmark.objects.filter(user=request.user, question=obj).exists()
        return False

    def get_saves_count(self, obj):
        return obj.bookmarked_by.count()

    def get_updated_by(self, obj):
        return obj.updated_by
