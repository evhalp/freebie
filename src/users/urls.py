from django.urls import include, path
from . import views

urlpatterns = [
    path('users/', include('django.contrib.auth.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/<str:username>', views.user_profile, name='user_profile'),
    path('sign_up/', views.sign_up, name='sign_up'),
]