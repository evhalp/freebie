from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from .forms import CustomUserCreationForm, UserProfileForm


def dashboard(request):
    return render(request, "users/dashboard.html")

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
