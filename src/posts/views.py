from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from .forms import PostCreationForm, PostImageFormSet
from users.models import User, UserProfile

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
    post_user = User.objects.get(username = post.user)
    profile = UserProfile.objects.get(user = post.user)

    if request.method == 'POST':
        # --- Follow Button ---
        if 'follow' in request.POST:
            action = request.POST['follow']
            if action == 'unfollow':
                print(request.user.username, 'UNFOLLOWING', post_user.username)
                request.user.userprofile.unfollow(profile)
            elif action == 'follow':
                print(request.user.username, 'FOLLOWING', post_user.username)
                request.user.userprofile.follow(profile)

        return redirect('posts', id=id)
    # --- Context ---
    context = {
        'post': post,
        'post_user': post_user,
        'profile' : profile
    }

    return render(request, 'posts/posts.html', context)