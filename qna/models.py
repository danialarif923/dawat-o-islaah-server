# qna/models.py
from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Question(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('answered', 'Answered'),
        ('approved', 'Approved'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=255)
    content = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    is_most_read = models.BooleanField(default=False)

    updated_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='updated_questions',
        limit_choices_to={'role': 'mufti'}
    )
    updated_by_manual = models.CharField(max_length=255, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def updated_by(self):
        if self.updated_by_user:
            full = self.updated_by_user.get_full_name()
            return full if full.strip() else self.updated_by_user.email
        return self.updated_by_manual or ''

class Answer(models.Model):
    APPROVAL_STATUS = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    mufti = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers')
    content = RichTextField()
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS, default='pending')

    updated_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='updated_answers',
        limit_choices_to={'role': 'mufti'}
    )
    updated_by_manual = models.CharField(max_length=255, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Answer to {self.question.title}"

    @property
    def updated_by(self):
        if self.updated_by_user:
            full = self.updated_by_user.get_full_name()
            return full if full.strip() else self.updated_by_user.email
        return self.updated_by_manual or ''

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')
        
    def __str__(self):
        return f"{self.user.email} saved {self.question.title}"
