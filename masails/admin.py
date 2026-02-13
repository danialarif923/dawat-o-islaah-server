from django.contrib import admin
from .models import Masail,Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

@admin.register(Masail)
class MasailAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'created_at', 'updated_at', 'image')  # Added 'image'
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'category', 'image')  # Added 'image'
        }),
        ('Publishing', {
            'fields': ('status',),
            'classes': ('wide',)
        }),
    )

    actions = ['make_published', 'make_draft']

    @admin.action(description='Mark selected masails as published')
    def make_published(self, request, queryset):
        queryset.update(status='published')

    @admin.action(description='Mark selected masails as draft')
    def make_draft(self, request, queryset):
        queryset.update(status='draft')