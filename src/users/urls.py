from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/<str:username>', views.user_profile, name='user_profile'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('change-email/', views.change_email, name='change_email'),
    path('toggle-follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
]