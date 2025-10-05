from django import forms

from core.models.user import User


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary",
                "placeholder": "Enter your email",
                "id": "email",
                "name": "email",
            }
        ),
    )

    password = forms.CharField(
        min_length=6,
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary",
                "placeholder": "Enter your password",
                "id": "password",
                "name": "password",
            }
        ),
    )

    remember_me = forms.BooleanField(
        label="Remember me",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "mr-2",
                "id": "remember_me",
                "name": "remember_me",
            }
        ),
    )


class RegistrationForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary",
                "placeholder": "Enter your email",
                "id": "email",
                "name": "email",
            }
        ),
    )
