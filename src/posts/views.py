from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, User
from .forms import PostCreationForm, PostImageFormSet
from users.models import UserProfile

@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostCreationForm(request.POST, request.FILES)
        formset = PostImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            form.save_m2m()

            images = formset.save(commit=False)
            for image in images:
                image.post = post
                image.save()

            return redirect('posts', id=post.id)
        else:
            messages.error(request, 'Form is invalid')
    else:
        form = PostCreationForm()
        formset = PostImageFormSet()

    context = {
        'form': form,
        'formset': formset,
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