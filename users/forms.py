# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    
    # ADD THESE CUSTOM FIELDS
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        initial='tourist'
    )
    nationality = forms.ChoiceField(
        choices=User.NATIONALITY_CHOICES,
        required=True,
        initial='singaporean'
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+65 1234 5678'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'user_type', 'nationality', 'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        # ADD THESE LINES TO SAVE CUSTOM FIELDS
        user.user_type = self.cleaned_data['user_type']
        user.nationality = self.cleaned_data['nationality']
        user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')