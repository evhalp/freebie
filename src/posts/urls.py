from django.urls import path
from .views import create_post_view, post_view, toggle_like_view, toggle_attend_view

urlpatterns = [
    path('create/', create_post_view, name='create_post'),
    path('<int:id>/', post_view, name='posts'),
    path('<int:id>/like/', toggle_like_view, name='post-like')
    ,
    path('<int:id>/attend/', toggle_attend_view, name='post-attend')
]