from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from .models import Question, Answer, Category, Bookmark

User = get_user_model()

class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mufti_qs = User.objects.filter(role='mufti')
        self.fields['updated_by_user'].queryset = mufti_qs
        self.fields['updated_by_user'].empty_label = '--- Select Mufti ---'
        self.fields['updated_by_user'].required = False
        self.fields['updated_by_manual'].required = False
        self.fields['updated_by_manual'].widget.attrs['placeholder'] = 'Or enter mufti name manually'

class AnswerAdminForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mufti_qs = User.objects.filter(role='mufti')
        self.fields['updated_by_user'].queryset = mufti_qs
        self.fields['updated_by_user'].empty_label = '--- Select Mufti ---'
        self.fields['updated_by_user'].required = False
        self.fields['updated_by_manual'].required = False
        self.fields['updated_by_manual'].widget.attrs['placeholder'] = 'Or enter mufti name manually'

class AnswerInline(admin.StackedInline):
    model = Answer
    form = AnswerAdminForm
    extra = 0
    fields = ('content', 'approval_status', ('updated_by_user', 'updated_by_manual'))

    def get_readonly_fields(self, request, obj=None):
        readonly = ('created_at', 'updated_at')
        if not request.user.is_superuser:
            readonly = readonly + ('approval_status',)
        return readonly

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Mufti').exists() and not request.user.is_superuser:
            return qs.filter(mufti=request.user)
        return qs

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    list_display = ('title', 'user', 'status', 'view_count', 'is_most_read', 'get_approval_status', 'created_at')
    list_filter = ('status', 'is_most_read', 'created_at')
    search_fields = ('title', 'content', 'user__email')
    inlines = [AnswerInline]
    fieldsets = [
        (None, {
            'fields': ('title', ('user', 'category'), 'content', 'status')
        }),
        ('Updated By', {
            'fields': (('updated_by_user', 'updated_by_manual'),),
            'classes': ('wide',),
        }),
        ('Stats', {
            'fields': ('view_count', 'download_count', 'is_most_read'),
            'classes': ('wide',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    ]
    readonly_fields = ('user', 'created_at', 'updated_at')

    class Media:
        js = ("js/ckeditor_font_loader.js",)

    def get_approval_status(self, obj):
        from django.core.exceptions import ObjectDoesNotExist
        try:
            return obj.answer.approval_status
        except ObjectDoesNotExist:
            return '-'
    get_approval_status.short_description = 'Answer Approval'

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('user', 'answer')
        if request.user.groups.filter(name='Mufti').exists() and not request.user.is_superuser:
            return qs.filter(status='pending')
        return qs

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        # Handle deletions
        for obj in formset.deleted_objects:
            obj.question.status = 'pending'
            obj.question.save()
            obj.delete()

        for instance in instances:
            if isinstance(instance, Answer):
                if not instance.pk:
                    instance.mufti = request.user
                instance.save()
                # Update question status based on answer
                question = instance.question
                if instance.approval_status == 'approved':
                    question.status = 'approved'
                elif instance.approval_status == 'rejected':
                    question.status = 'pending'
                else:
                    question.status = 'answered'
                question.save()

        formset.save_m2m()


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    form = AnswerAdminForm
    list_display = ('question', 'mufti', 'approval_status', 'get_updated_by', 'created_at')
    list_filter = ('approval_status', 'created_at')
    search_fields = ('content', 'question__title')
    fieldsets = [
        (None, {
            'fields': ('question', 'mufti', 'content', 'approval_status')
        }),
        ('Updated By', {
            'fields': (('updated_by_user', 'updated_by_manual'),),
            'classes': ('wide',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    ]
    readonly_fields = ('mufti', 'question', 'created_at', 'updated_at')
    actions = ['approve_answers', 'reject_answers']

    class Media:
        js = ("js/ckeditor_font_loader.js",)

    def get_updated_by(self, obj):
        return obj.updated_by
    get_updated_by.short_description = 'Updated By'

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('question', 'mufti')
        if request.user.groups.filter(name='Mufti').exists() and not request.user.is_superuser:
            return qs.filter(mufti=request.user)
        return qs

    @admin.action(description='Approve selected answers')
    def approve_answers(self, request, queryset):
        queryset.update(approval_status='approved')
        for answer in queryset:
            answer.question.status = 'approved'
            answer.question.save()
        self.message_user(request, f'{queryset.count()} answers approved.')

    @admin.action(description='Reject selected answers')
    def reject_answers(self, request, queryset):
        for answer in queryset:
            answer.question.status = 'pending'
            answer.question.save()
        queryset.update(approval_status='rejected')
        self.message_user(request, f'{queryset.count()} answers rejected.')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'created_at')
