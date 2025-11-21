from django.urls import path
from .views import edit_post_view, post_view, toggle_like_view

urlpatterns = [
    path('<int:id>/', post_view, name='posts'),
    path('create/', edit_post_view, name='create_post'),
    path('<int:id>/edit/', edit_post_view, name='edit_post'),
    path('<int:id>/like/', toggle_like_view, name='like_post')
]