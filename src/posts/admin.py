from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'description_preview', 'location', 'start_time', 'created_at']
    list_filter = ['created_at', 'start_time']
    search_fields = ['title', 'description', 'location', 'user__username']

    def description_preview(self, obj):
        return f'{obj.description[:50]}...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'