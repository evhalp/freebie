from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user__username', 'bio_preview', 'credibility', 'followers_count', 'following_count']
    search_fields = ['user__username']
    list_filter = ['credibility']
    filter_horizontal = ['following']

    def bio_preview(self, obj):
        return f'{obj.bio[:50]}...' if len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'Biography'

    def followers_count(self, obj):
        return obj.followers.count()
    followers_count.short_description = 'Followers'

    def following_count(self, obj):
        return obj.following.count()
    following_count.short_description = 'Following'