from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user__username', 'bio_preview', 'credibility']
    search_fields = ['user__username']

    def bio_preview(self, obj):
        return f'{obj.bio[:50]}...' if len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'Biography'
