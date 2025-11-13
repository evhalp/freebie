from django import forms
from .models import Post, PostImage

class PostCreationForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'description', 'location', 'start_time', 'end_time', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post description',
                'rows': 5
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter location'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
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
                'class': 'form-control'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional caption'
            })
        }

PostImageFormSet = forms.inlineformset_factory(
    Post,
    PostImage,
    form=PostImageForm,
    extra=3,
    can_delete=False
)