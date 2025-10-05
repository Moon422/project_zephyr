from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "glass-input w-full", "placeholder": "Enter your email"}
        ),
    )

    password = forms.CharField(
        min_length=6,
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "glass-input w-full", "placeholder": "Enter your password"}
        ),
    )

    remember_me = forms.BooleanField(
        label="Remember me",
        widget=forms.CheckboxInput(attrs={"class": "w-4 h-4 rounded"}),
    )
