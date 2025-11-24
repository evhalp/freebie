from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Reaction, PostImage
from .forms import PostCreationForm, PostImageFormSet
from users.models import User, UserProfile
from users.weights import adjust_credibility, W_LIKE, W_ATTEND, W_POSTS

@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostCreationForm(request.POST, request.FILES)
        post = None
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            form.save_m2m()
        else:
            # If the main form is invalid, re-render with an empty image formset
            formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.none())
            context = {'form': form, 'formset': formset, 'user': request.user}
            return render(request, 'posts/create_post.html', context)

        # Bind the POSTed image forms to the newly created post instance
        formset = PostImageFormSet(request.POST, request.FILES, instance=post)
        # Debug: print request.FILES and formset form info to server console
        print('DEBUG: request.FILES keys:', list(request.FILES.keys()))
        print('DEBUG: total_forms:', formset.total_form_count())
        formset_forms = list(formset.forms)
        for i, f in enumerate(formset_forms):
            try:
                changed = f.has_changed()
            except Exception:
                changed = 'err'
            print(f'DEBUG: form {i} has_changed={changed} errors={f.errors if f.errors else None}')

        if formset.is_valid():
            # Let the formset save and attach images to `post`
            saved_objs = formset.save()
            print('DEBUG: saved objects count:', len(saved_objs))
            # Apply post creation penalty to the author's credibility
            try:
                adjust_credibility(request.user, -W_POSTS)
            except Exception:
                # don't block post creation if this errors for some reason
                pass
            return redirect('posts', id=post.id)
        else:
            # Provide detailed formset errors to help debugging/feedback
            print('DEBUG: formset.errors:', formset.errors)
            messages.error(request, 'Image form is invalid')
    else:
        form = PostCreationForm()
        formset = PostImageFormSet(queryset=PostImage.objects.none())

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
        # increment author's credibility
        try:
            adjust_credibility(post.user, W_LIKE)
        except Exception:
            pass
    else:
        # toggle: if already LIKE -> remove sentiment; otherwise set to LIKE
        if reaction.sentiment == 'LIKE':
            reaction.sentiment = None
            try:
                adjust_credibility(post.user, -W_LIKE)
            except Exception:
                pass
        else:
            reaction.sentiment = 'LIKE'
            try:
                adjust_credibility(post.user, W_LIKE)
            except Exception:
                pass
        reaction.save()

    return redirect('posts', id=id)


@login_required
def toggle_attend_view(request, id):
    """Toggle the is_attending flag for the logged-in user on the given post.

    Creates a Reaction if one doesn't exist and toggles the is_attending boolean.
    Adjusts the post author's credibility accordingly.
    """
    if request.method != 'POST':
        return redirect('posts', id=id)

    post = get_object_or_404(Post, id=id)

    reaction, created = Reaction.objects.get_or_create(post=post, user=request.user)

    if created:
        reaction.is_attending = True
        reaction.save()
        try:
            adjust_credibility(post.user, W_ATTEND)
        except Exception:
            pass
    else:
        if reaction.is_attending:
            reaction.is_attending = False
            try:
                adjust_credibility(post.user, -W_ATTEND)
            except Exception:
                pass
        else:
            reaction.is_attending = True
            try:
                adjust_credibility(post.user, W_ATTEND)
            except Exception:
                pass
        reaction.save()

    return redirect('posts', id=id)