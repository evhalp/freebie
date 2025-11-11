from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from .forms import CustomUserCreationForm, UserProfileForm


def dashboard(request):
    return render(request, "users/dashboard.html")

@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user and request.method == 'POST':
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
