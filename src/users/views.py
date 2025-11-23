from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
import json
from django.http import JsonResponse

from .forms import CustomUserCreationForm, UserProfileForm
from posts.models import Post
from django.db.models import Count, Q
from django.db.models.functions import Lower


def dashboard(request):
    context = {}
    
    if request.user.is_authenticated:
        # User's own posts with pagination (2 per page)
        user_posts_all = Post.objects.filter(user=request.user).order_by('-created_at')
        paginator = Paginator(user_posts_all, 2)
        page_number = request.GET.get('posts_page', 1)
        user_posts_page = paginator.get_page(page_number)
        
        now = timezone.now()
        # Single hot event: not user's own, happening now, most liked; tie-breaker: earliest end_time
        hot_event_qs = (
            Post.objects.exclude(user=request.user)
            .filter(start_time__lte=now, end_time__gte=now)
            .annotate(
                like_count=Count('reactions', filter=Q(reactions__sentiment='LIKE'), distinct=True)
            )
            .order_by('-like_count', 'end_time')
        )
        hot_event = hot_event_qs.first()
        
        # Following list - exclude self, order alphabetically by username
        following_users = (
            request.user.userprofile.following
            .exclude(user=request.user)
            .select_related('user')
            .order_by(Lower('user__username'))
        )
        
        # Feed from people user follows
        following_ids = request.user.userprofile.following.values_list('user__id', flat=True)
        following_feed = (
            Post.objects.filter(user__id__in=following_ids)
            .annotate(like_count=Count('reactions', filter=Q(reactions__sentiment='LIKE'), distinct=True))
            .order_by('-created_at')[:8]
        )
        
        # Prepare feed data for JSON injection
        feed_data = []
        for post in following_feed:
            image_obj = post.images.first()  # call the method to get first image (was missing parentheses)
            if image_obj and getattr(image_obj, 'image', None) and getattr(image_obj.image, 'name', None):
                image_url = image_obj.image.url
            else:
                image_url = settings.MEDIA_URL + 'default.png'
            # Author avatar (if present)
            author_profile = getattr(post.user, 'userprofile', None)
            if author_profile and getattr(author_profile, 'image', None):
                author_image = author_profile.image.url
            else:
                author_image = settings.MEDIA_URL + 'default.png'
            feed_data.append({
                'id': post.id,
                'url': reverse('posts', args=[post.id]),
                'title': post.title,
                'location': post.location or '',
                'description': post.description,
                'image': image_url,
                'date': post.start_time.strftime('%B %d, %Y'),
                # Accurate like count per post
                'like_count': post.reactions.filter(sentiment='LIKE').count(),
                # Whether current user liked the post
                'user_liked': post.reactions.filter(user=request.user, sentiment='LIKE').exists(),
                'author_username': post.user.username,
                'author_url': reverse('user_profile', args=[post.user.username]),
                'author_image': author_image,
                'created_at': post.created_at.isoformat(),
                'tags': [
                    {
                        'name': t.name,
                        'bg': t.bg_color,
                        'text': t.text_color
                    } for t in post.tags.all()[:3]
                ]
            })
        feed_data_json = json.dumps(feed_data)
        
        # Prepare attending posts data for carousel
        attending_posts = (
            Post.objects.filter(reactions__user=request.user, reactions__is_attending=True)
            .annotate(like_count=Count('reactions', filter=Q(reactions__sentiment='LIKE'), distinct=True))
            .order_by('start_time')
        )
        attending_data = []
        for post in attending_posts:
            image_obj = post.images.first()
            if image_obj and getattr(image_obj, 'image', None) and getattr(image_obj.image, 'name', None):
                image_url = image_obj.image.url
            else:
                image_url = settings.MEDIA_URL + 'default.png'
            attending_data.append({
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
            })
        attending_data_json = json.dumps(attending_data)
        
        context = {
            'user_posts_page': user_posts_page,
            'hot_event': hot_event,
            'following_users': following_users,
            'following_feed': following_feed,
            'feed_data': feed_data,
            'feed_data_json': feed_data_json,
            'attending_posts': attending_posts,
            'attending_data_json': attending_data_json
        }
    
    return render(request, "users/dashboard.html", context)

@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user and request.method == 'POST':
        if request.POST.get('image-clear') and not request.FILES.get('image'):
            profile_user.userprofile.image.delete(save=False)
            profile_user.userprofile.image = None
            profile_user.userprofile.save()
            if 'bio' in request.POST:
                profile_user.userprofile.bio = request.POST.get('bio', '')
                profile_user.userprofile.save()
            return redirect('user_profile', username=username)
        
        if request.POST.get('image-clear') and request.FILES.get('image'):
            pass
        
        form = UserProfileForm(request.POST, request.FILES, instance=profile_user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('user_profile', username=username)
    else:
        form = UserProfileForm(instance=profile_user.userprofile)

    context = {
        'profile_user': profile_user,
        'form': form
    }

    return render(request, 'users/user_profile.html', context)

def sign_up(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("dashboard"))
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/sign_up.html", {"form": form})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was changed successfully!')
            return render(request, 'registration/password_change_form.html', {'form': PasswordChangeForm(request.user)})
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_change_form.html', {'form': form})

@login_required
def change_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        confirm_email = request.POST.get('confirm_email')
        
        if new_email != confirm_email:
            messages.error(request, 'Email addresses do not match.', extra_tags='email')
        elif User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
            messages.error(request, 'This email address is already in use.', extra_tags='email')
        else:
            request.user.email = new_email
            request.user.save()
            messages.success(request, 'Your email was updated successfully!', extra_tags='email')
        
        return redirect('user_profile', username=request.user.username)
    
    return redirect('user_profile', username=request.user.username)

@login_required
def toggle_follow(request, username):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        target_user = get_object_or_404(User, username=username)
        
        if target_user == request.user:
            return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
        
        user_profile = request.user.userprofile
        target_profile = target_user.userprofile
        
        if user_profile.is_following(target_profile):
            user_profile.unfollow(target_profile)
            is_following = False
        else:
            user_profile.follow(target_profile)
            is_following = True
        
        return JsonResponse({
            'is_following': is_following,
            'followers_count': target_profile.followers.count()
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
