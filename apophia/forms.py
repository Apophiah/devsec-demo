import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Profile

# Matches the opening of any HTML tag, e.g. <script, <img, </a.
# Plain text that happens to contain "<" followed by a digit or punctuation
# (e.g. "x<3") is not flagged.
_HTML_TAG_RE = re.compile(r'<[a-zA-Z/]')


def _validate_no_html(value):
    if _HTML_TAG_RE.search(value):
        raise ValidationError("HTML tags are not allowed in this field.")


class ApophiaUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Informative email address.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '')
        _validate_no_html(bio)
        return bio

    def clean_location(self):
        location = self.cleaned_data.get('location', '')
        _validate_no_html(location)
        return location

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
