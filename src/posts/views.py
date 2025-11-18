from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Reaction
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
    post = get_object_or_404(Post, id=id)
    user = post.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = None

    # like count and whether current user liked
    like_count = post.reactions.filter(sentiment='LIKE').count()
    user_liked = False
    if request.user.is_authenticated:
        user_liked = post.reactions.filter(user=request.user, sentiment='LIKE').exists()

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
        'user': user,
        "profile": profile,
        "like_count": like_count,
        "user_liked": user_liked,
    }

    return render(request, 'posts/posts.html', context)


@login_required
def toggle_like_view(request, id):
    """Toggle a LIKE reaction for the logged-in user on the given post.

    - If the user has no Reaction for the post, create one with sentiment='LIKE'.
    - If the user has a Reaction with sentiment='LIKE', clear the sentiment (unlike).
    - If the user has a Reaction with a different sentiment, set it to 'LIKE'.

    Redirects back to the post detail page.
    """
    if request.method != 'POST':
        return redirect('posts', id=id)

    post = get_object_or_404(Post, id=id)

    reaction, created = Reaction.objects.get_or_create(post=post, user=request.user)

    if created:
        reaction.sentiment = 'LIKE'
        reaction.save()
    else:
        # toggle: if already LIKE -> remove sentiment; otherwise set to LIKE
        if reaction.sentiment == 'LIKE':
            reaction.sentiment = None
        else:
            reaction.sentiment = 'LIKE'
        reaction.save()

    return redirect('posts', id=id)