from django import forms
from .models import UploadedFile, UserProfile
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'department', 'position', 'education', 'research_interests', 'profile_photo', 'email']