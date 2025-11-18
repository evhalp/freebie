from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("first_name", "last_name", "email",)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'cols': 50})
        }

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Username not found or incorrect password.",
        'inactive': "This account is inactive.",
    }
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            if not User.objects.filter(username=username).exists():
                raise ValidationError(
                    "Username not found.",
                    code='invalid_login',
                )
            
            self.user_cache = self.get_user()
            if self.user_cache is None:
                raise ValidationError(
                    "Incorrect password.",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class CustomPasswordChangeForm(PasswordChangeForm):
    error_messages = {
        'password_incorrect': "The old password you entered is incorrect.",
        'password_mismatch': "The two password fields didn't match.",
    }