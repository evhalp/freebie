from django.shortcuts import render
from posts.models import Post, User
from users.models import  UserProfile



    

def post_view(request, id):

    """Loads Post information related to specified id"""
    # --- Base queryset ---
    post = Post.objects.get(id=id)
    user = User.objects.get(username = post.user)
    profile = UserProfile.objects.get(user = user)

    # --- Context ---
    context = {
        'post': post,
        'user': user,
        "profile" : profile
    }

    return render(request, 'posts/posts.html', context)