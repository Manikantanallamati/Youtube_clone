from django import forms
from .models import Video, Comment

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'file', 'description', 'thumbnail', 'category']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
