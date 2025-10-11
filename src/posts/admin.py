from django.contrib import admin
from django.utils.html import format_html
from .models import Tag, Post, Comment

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color_preview', 'description']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 15px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.color
        )
    color_preview.short_description = 'Color'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'description_preview', 'location', 'start_time', 'created_at']
    list_filter = ['created_at', 'start_time']
    search_fields = ['title', 'description', 'location', 'user__username']

    def description_preview(self, obj):
        return f'{obj.description[:50]}...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'

@admin.register(Comment)
class PostComment(admin.ModelAdmin):
    list_display = ['post', 'user', 'content_preview', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username', 'post__title']
    raw_id_fields = ['post', 'user', 'parent']

    def content_preview(self, obj):
        return f'{obj.content[:50]}...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'