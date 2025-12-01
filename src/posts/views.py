from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Reaction, PostImage
from .forms import PostCreationForm, PostImageFormSet
from users.models import UserProfile

@login_required
def edit_post_view(request, id=None):

    if id is not None:
        post = get_object_or_404(Post, id=id)
        if post.user != request.user:
            print(post.user, request.user)
            return redirect('posts', id=id)
        is_editing = True
    else:
        post = None
        is_editing = False

    if request.method == 'POST':

        # Handle post deletion
        if is_editing and 'delete' in request.POST:
            post.delete()
            messages.success(request, "Post deleted successfully.")
            return redirect('dashboard')
         
        # Handle post creation/editing
        form = PostCreationForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            form.save_m2m()

            formset = PostImageFormSet(request.POST, request.FILES, instance=post)
            if formset.is_valid():
                formset.save()

            return redirect('posts', id=post.id)
        else:
            if is_editing:
                formset = PostImageFormSet(request.POST, request.FILES, instance=post)
            else:
                formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.none())
            context = {
                'form': form, 
                'formset': formset, 
                'user': request.user, 
                'post': post, 
                'is_editing': is_editing
            }
            return render(request, 'posts/edit_post.html', context)
    else:
        if is_editing:
            form = PostCreationForm(instance=post)
            formset = PostImageFormSet(instance=post)
        else:
            form = PostCreationForm()
            formset = PostImageFormSet(queryset=PostImage.objects.none())    

    context = {
        'form': form, 
        'formset': formset, 
        'user': request.user, 
        'post': post, 
        'is_editing': is_editing
    }
    return render(request, 'posts/edit_post.html', context)

def post_view(request, id):

    """Loads Post information related to specified id"""
    # --- Base queryset ---
    post = get_object_or_404(Post, id=id)
    post_author = post.user
    try:
        profile = UserProfile.objects.get(user=post_author)
    except UserProfile.DoesNotExist:
        profile = None

    # like count and whether current user liked
    like_count = post.reactions.filter(sentiment='LIKE').count()
    user_liked = False
    if request.user.is_authenticated:
        user_liked = post.reactions.filter(user=request.user, sentiment='LIKE').exists()

    # attending count and whether current user is attending
    attending_count = post.reactions.filter(is_attending=True).count()
    user_is_attending = False
    if request.user.is_authenticated:
        user_is_attending = post.reactions.filter(user=request.user, is_attending=True).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'follow_toggle' in request.POST and profile and request.user != post_author:
            actor_profile = request.user.userprofile
            target_profile = profile
            if actor_profile.is_following(target_profile):
                actor_profile.unfollow(target_profile)
                messages.success(request, f"You unfollowed {post_author.username}.")
            else:
                actor_profile.follow(target_profile)
                messages.success(request, f"You followed {post_author.username}.")
            return redirect('posts', id=id)

    is_following = False
    if request.user.is_authenticated and request.user != post_author and profile:
        is_following = request.user.userprofile.is_following(profile)
    # --- Context ---
    context = {
        'post': post,
        'author': post_author,
        'profile': profile,
        'like_count': like_count,
        'user_liked': user_liked,
        'attending_count': attending_count,
        'user_is_attending': user_is_attending,
        'is_following': is_following,
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


@login_required
def toggle_attend_view(request, id):
    """Toggle the is_attending flag for the logged-in user on the given post.

    - If the user has no Reaction for the post, create one and set is_attending=True.
    - Otherwise toggle the boolean and save.

    Redirects back to the post detail page.
    """
    if request.method != 'POST':
        return redirect('posts', id=id)

    post = get_object_or_404(Post, id=id)

    reaction, created = Reaction.objects.get_or_create(post=post, user=request.user)

    # Toggle attending flag
    reaction.is_attending = not bool(reaction.is_attending)
    reaction.save()

    return redirect('posts', id=id)