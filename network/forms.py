from django.forms import ModelForm, HiddenInput
from .models import User, Post
from django.forms.widgets import Textarea

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['message']
        labels = {"message": "",}
        widgets = {
            'message': Textarea(attrs={ 'placeholder': 'Type your post here',
                                        'id': 'postMessageTextArea',
                                        'class': 'form-control',
                                        }),
        }