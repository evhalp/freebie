from django import forms
from .models import Post, PostImage, Comment

class PostCreationForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'description', 'location', 'start_time', 'end_time', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter post title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'style': 'resize: none;',
                'placeholder': 'Enter post description',
                'rows': 1,
                'cols': 1,
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter location',
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-time-input',
                'type': 'datetime-local',
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-time-input',
                'type': 'datetime-local',
            }),
            'tags': forms.CheckboxSelectMultiple()
        }
        labels = {
            'title': 'Post Title',
            'description': 'Description',
            'location': 'Location',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'tags': 'Tags'
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError(
                    "Event's end time must be after start time"
                )
        
        return cleaned_data
    
class PostImageForm(forms.ModelForm):
    
    class Meta:
        model = PostImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-image-input',
            }),
            'caption': forms.TextInput(attrs={
                'class': 'label-and-input',
                'placeholder': 'Image Caption',
                'style' : 'width: 100%;'
                "padding: 0.5rem;"
                'border: 1px solid #ccc; '
                'border-radius: 5px;'
                'font-family: Arial, sans-serif; '
                'font-size: 1rem;'
                'width: 100%;'
            })
        }
        labels = {
            'image': 'Image',
            'caption': 'Caption',
        }

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'style': 'resize: none;',
                'placeholder': 'Enter comment...',
                'rows': 5,
                'cols': 40,
            })
        }
        labels = {
            'content': ''
        }

PostImageFormSet = forms.inlineformset_factory(
    Post,
    PostImage,
    form=PostImageForm,
    extra=5,
    can_delete=True
)