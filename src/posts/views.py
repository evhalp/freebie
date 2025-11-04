from django.shortcuts import render
from posts.models import Post, User



    

def post_view(request, id):

    """Loads Post information related to specified id"""
    # --- Base queryset ---
    post = Post.objects.get(id=id)
    user = User.objects.get(username = post.user)

    # --- Context ---
    context = {
        'post': post,
        'user': user
    }

    return render(request, 'posts/posts.html', context)