from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label='Username',
        help_text='',
        max_length=25,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username-input'}),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        max_length=25,
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if len(password1) > 20:
            raise ValidationError("Password can't be longer than 20 characters.")
        if not any(char.isdigit() for char in password1):
            raise ValidationError("Password must contain at least 1 digit.")
        if not any(char.islower() for char in password1):
            raise ValidationError("Password must contain at least 1 lowercase letter.")
        if not any(char.isupper() for char in password1):
            raise ValidationError("Password must contain at least 1 uppercase letter.")
        return password1


class AuthorizationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthorizationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user_queryset = User.objects.filter(username=username)
            if not user_queryset.exists():
                raise forms.ValidationError("Invalid username.")

            user = user_queryset.first()

            if not user.check_password(password):
                raise forms.ValidationError("Invalid password.")
            if not user.is_active:
                raise forms.ValidationError("User is not active.")
        return self.cleaned_data



class OrderFilterForm(forms.Form):
    SORT_CHOICES = (
        ('price_low_to_high', 'Price: Low to High'),
        ('price_high_to_low', 'Price: High to Low'),
    )

    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False)
    min_price = forms.DecimalField(label='Min Price', required=False)
    max_price = forms.DecimalField(label='Max Price', required=False)