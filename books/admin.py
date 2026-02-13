from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uploaded_at', 'is_public')
    list_filter = ('is_public', 'uploaded_at')
    search_fields = ('title', 'author', 'description')
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)

    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'description')
        }),
        ('Files', {
            'fields': ('pdf_file', 'cover_image')
        }),
        ('Visibility', {
            'fields': ('is_public',),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_public', 'make_private']

    @admin.action(description='Mark selected books as public')
    def make_public(self, request, queryset):
        queryset.update(is_public=True)

    @admin.action(description='Mark selected books as private')
    def make_private(self, request, queryset):
        queryset.update(is_public=False)