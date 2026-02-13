# qna/admin.py
from django.contrib import admin
from .models import Question, Answer

class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0
    fields = ('content', 'approval_status')
    readonly_fields = ('mufti', 'created_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Mufti').exists():
            return qs.filter(mufti=request.user)
        return qs

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'content', 'user__email')
    inlines = [AnswerInline]
    readonly_fields = ('user', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Mufti').exists():
            return qs.filter(status='pending')
        return qs

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Answer):
                if not instance.pk:  # New answer
                    instance.mufti = request.user
                    instance.question.status = 'answered'
                    instance.question.save()
                instance.save()
        formset.save_m2m()

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'mufti', 'approval_status', 'created_at')
    list_filter = ('approval_status', 'created_at')
    search_fields = ('content', 'question__title')
    readonly_fields = ('mufti', 'question', 'created_at', 'updated_at')
    actions = ['approve_answers', 'reject_answers']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Mufti').exists():
            return qs.filter(mufti=request.user)
        return qs

    @admin.action(description='Approve selected answers')
    def approve_answers(self, request, queryset):
        queryset.update(approval_status='approved')
        for answer in queryset:
            answer.question.status = 'approved'
            answer.question.save()

    @admin.action(description='Reject selected answers')
    def reject_answers(self, request, queryset):
        queryset.update(approval_status='rejected')
        for answer in queryset:
            answer.question.status = 'pending'
            answer.question.save()
            answer.delete()