from django.contrib import admin
from django.utils.html import format_html
from .models import Tag, Post, Comment, Reaction

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color_preview', 'description']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 5px 15px; border-radius: 3px;">{}</span>',
            obj.bg_color,
            obj.text_color,
            obj.name
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
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'content_preview', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username', 'post__title']
    raw_id_fields = ['post', 'user', 'parent']

    def content_preview(self, obj):
        return f'{obj.content[:50]}...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'sentiment', 'is_attending', 'created_at']
    list_filter = ['sentiment', 'is_attending', 'created_at']
    search_fields = ['user__username', 'post__title']
    raw_id_fields = ['post', 'user']
