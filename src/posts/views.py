from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Post, User
from .forms import PostCreationForm
from users.models import  UserProfile

def create_post_view(request):
    if request.method == 'POST':
        form = PostCreationForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            form.save_m2m()

            return redirect('posts', id=post.id)
        else:
            messages.error(request, 'Form is invalid')
    else:
        form = PostCreationForm()

    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'posts/create_post.html', context)

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