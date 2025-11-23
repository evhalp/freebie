from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Reaction, PostImage
from .forms import PostCreationForm, PostImageFormSet
from users.models import User, UserProfile

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
        if 'attend_toggle' in request.POST:
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
        'is_following': is_following,
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
    else:
        if reaction.sentiment == 'LIKE':
            reaction.sentiment = None
        else:
            reaction.sentiment = 'LIKE'
        reaction.save()

    like_count = post.reactions.filter(sentiment='LIKE').count()
    user_liked = post.reactions.filter(user=request.user, sentiment='LIKE').exists()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'like_count': like_count, 'user_liked': user_liked})

    return redirect('posts', id=id)

@login_required
def toggle_attending_view(request, id):
    if request.method != 'POST':
        return redirect('posts', id=id)
    post = get_object_or_404(Post, id=id)
    reaction, _ = Reaction.objects.get_or_create(post=post, user=request.user)
    reaction.is_attending = not reaction.is_attending
    reaction.save()
    # Build a serialized post representation for AJAX consumers so the
    # frontend can add/remove items from the My Attending list without a full reload.
    image_obj = post.images.first()
    if image_obj and getattr(image_obj, 'image', None) and getattr(image_obj.image, 'name', None):
        image_url = image_obj.image.url
    else:
        from django.conf import settings
        image_url = settings.MEDIA_URL + 'default.png'

    post_data = {
        'id': post.id,
        'url': reverse('posts', args=[post.id]),
        'title': post.title,
        'location': post.location or '',
        'description': post.description,
        'image': image_url,
        'date': post.start_time.strftime('%B %d, %Y'),
        'like_count': post.reactions.filter(sentiment='LIKE').count(),
        'user_liked': post.reactions.filter(user=request.user, sentiment='LIKE').exists(),
        'tags': [
            {
                'name': t.name,
                'bg': t.bg_color,
                'text': t.text_color
            } for t in post.tags.all()[:3]
        ]
    }

    return JsonResponse({'is_attending': reaction.is_attending, 'post': post_data})