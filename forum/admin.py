from django.contrib import admin
from .models import Question, Answer

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

class FontLoaderMixin:
    class Media:
        js = ("js/ckeditor_font_loader.js",)

@admin.register(Question)
class QuestionAdmin(FontLoaderMixin, admin.ModelAdmin):
    list_display = ("title", "topic", "author", "votes", "created_at")
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(FontLoaderMixin, admin.ModelAdmin):
    list_display = ("question", "author", "votes", "created_at")