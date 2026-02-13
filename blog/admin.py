from django.contrib import admin
from .models import BlogPost,Comment

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at', 'status')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content')
        }),
        ('Media', {
            'fields': ('featured_image',),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('status',),
            'classes': ('wide',)
        }),
    )

    actions = ['make_published', 'make_draft']

    @admin.action(description='Mark selected posts as published')
    def make_published(self, request, queryset):
        queryset.update(status='published')

    @admin.action(description='Mark selected posts as draft')
    def make_draft(self, request, queryset):
        queryset.update(status='draft')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_content', 'user_email', 'blog_post_title', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'blog_post__status')
    search_fields = ('content', 'user__email', 'blog_post__title')
    list_editable = ('is_active',)
    list_select_related = ('user', 'blog_post')
    date_hierarchy = 'created_at'
    actions = ['approve_comments', 'disapprove_comments']

    def truncated_content(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    truncated_content.short_description = 'Content'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'

    def blog_post_title(self, obj):
        return obj.blog_post.title
    blog_post_title.short_description = 'Blog Post'
    blog_post_title.admin_order_field = 'blog_post__title'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'blog_post')

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} comments approved successfully.')

    @admin.action(description='Disapprove selected comments')
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} comments disapproved and hidden.')

    # Control what fields are shown in edit view
    fieldsets = (
        (None, {
            'fields': ('content', 'is_active')
        }),
        ('Relationships', {
            'fields': ('user', 'blog_post'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'user', 'blog_post')