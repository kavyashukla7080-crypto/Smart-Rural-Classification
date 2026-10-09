from django import forms
from users.models import UserRegistrationModel


class UserRegistrationForm(forms.ModelForm):

    Username = forms.CharField(
        widget=forms.TextInput(attrs={
            'pattern': r'[a-zA-Z\s]+',
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'title': 'Letters and spaces only'
        }),
        required=True,
        max_length=100
    )

    loginid = forms.CharField(
        widget=forms.TextInput(attrs={
            'pattern': r'[a-zA-Z0-9_]+',
            'class': 'form-control',
            'placeholder': 'Enter unique Login ID',
            'title': 'Letters, numbers, and underscores only'
        }),
        required=True,
        max_length=100
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create password (min 6 chars)',
            'minlength': '6',
        }),
        required=True,
        max_length=100
    )

    mobile = forms.CharField(
        widget=forms.TextInput(attrs={
            'pattern': r'[0-9]{10}',
            'class': 'form-control',
            'placeholder': 'Enter 10-digit mobile number',
            'title': 'Must be 10 digits'
        }),
        required=True,
        max_length=100
    )

    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
        }),
        required=True,
        max_length=100
    )

    locality = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter village / locality',
        }),
        required=True,
        max_length=100
    )

    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Enter full street / residential address',
        }),
        required=True,
        max_length=250
    )

    city = forms.CharField(
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'pattern': r'[A-Za-z\s]+',
            'title': 'Enter characters only',
            'class': 'form-control',
            'placeholder': 'Enter city / district',
        }),
        required=True,
        max_length=100
    )

    state = forms.CharField(
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'pattern': r'[A-Za-z\s]+',
            'title': 'Enter characters only',
            'class': 'form-control',
            'placeholder': 'Enter state',
        }),
        required=True,
        max_length=100
    )

    status = forms.CharField(
        widget=forms.HiddenInput(),
        initial='waiting',
        required=False,
        max_length=100
    )

    class Meta:
        model = UserRegistrationModel
        fields = '__all__'
