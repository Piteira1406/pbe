from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ClienteRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(max_length=15)
    address = forms.CharField(max_length=255)

class FornecedorRegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=15)
    supplier_name = forms.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']