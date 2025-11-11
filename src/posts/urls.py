from django.urls import path
from .views import create_post_view, post_view

urlpatterns = [
    path('create/', create_post_view, name='create_post'),
    path('<int:id>/', post_view, name='posts')
]