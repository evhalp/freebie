from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Reaction, PostImage, Comment
from users.models import User, UserProfile
from .forms import PostCreationForm, PostImageFormSet, CommentForm
from users.weights import adjust_credibility, W_LIKE, W_ATTEND, W_POSTS

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
    post = get_object_or_404(Post, id=id)
    post_author = post.user
    try:
        profile = UserProfile.objects.get(user=post_author)
    except UserProfile.DoesNotExist:
        profile = None

    like_count = post.reactions.filter(sentiment='LIKE').count()
    user_liked = False
    if request.user.is_authenticated:
        user_liked = post.reactions.filter(user=request.user, sentiment='LIKE').exists()

    # attending count and whether current user is attending
    attending_count = post.reactions.filter(is_attending=True).count()
    user_is_attending = False
    if request.user.is_authenticated:
        user_is_attending = post.reactions.filter(user=request.user, is_attending=True).exists()

    # Comments
    comments = post.comments.filter(parent=None).select_related('user')
    comment_form = CommentForm()

    if request.method == 'POST' and request.user.is_authenticated:
        # follow button
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
        # comments
        elif 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.user = request.user

                parent_id = request.POST.get('parent_id')
                if parent_id:
                    try:
                        parent_comment = Comment.objects.get(id=parent_id)
                        comment.parent = parent_comment
                    except:
                        pass

                comment.save()
                return redirect('posts', id=id)
        elif 'comment_delete' in request.POST:
            comment_id = request.POST.get('comment_id')
            try:
                comment = Comment.objects.get(id=comment_id, user=request.user)
                comment.delete()
            except Comment.DoesNotExist:
                pass
        elif 'attend_toggle' in request.POST:
            reaction, _ = Reaction.objects.get_or_create(post=post, user=request.user)
            reaction.is_attending = not reaction.is_attending
            reaction.save()
            if reaction.is_attending:
                messages.success(request, 'Marked as attending.')
            else:
                messages.success(request, 'Removed attending status.')
            return redirect('posts', id=id)

    is_following = False
    if request.user.is_authenticated and request.user != post_author and profile:
        is_following = request.user.userprofile.is_following(profile)
    context = {
        'post': post,
        'author': post_author,
        'profile': profile,
        'like_count': like_count,
        'user_liked': user_liked,
        'attending_count': attending_count,
        'is_following': is_following,
        'comments': comments,
        'comment_form': comment_form,
        'is_attending': Reaction.objects.filter(post=post, user=request.user, is_attending=True).exists() if request.user.is_authenticated else False,
    }

    return render(request, 'posts/posts.html', context)


@login_required
def toggle_like_view(request, id):

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

