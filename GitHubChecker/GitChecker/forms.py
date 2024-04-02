from typing import Any, Mapping
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import inlineformset_factory
from .models import Repository, TestParameters

class UserForm(forms.Form):
    username = forms.CharField(max_length=64)
    password = forms.CharField(max_length=64, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'bg-dark text-white'
        self.fields['password'].widget.attrs['class'] = 'bg-dark text-white'        

class RegForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2'] 

    def __init__(self, *args, **kwargs):
        super(RegForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'bg-dark text-white'
        self.fields['email'].widget.attrs['class'] = 'bg-dark text-white'
        self.fields['password1'].widget.attrs['class'] = 'bg-dark text-white'
        self.fields['password2'].widget.attrs['class'] = 'bg-dark text-white'

class RepoDetailForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['test_dir', 'test_command']

    def __init__(self, *args, **kwargs):
        super(RepoDetailForm, self).__init__(*args, **kwargs)
        self.fields['test_dir'].label = 'Test folder'
        self.fields['test_command'].label = 'Executable command'
        
        self.fields['test_dir'].widget.attrs['class'] = 'repository-col-input bg-dark text-white'
        self.fields['test_command'].widget.attrs['class'] = 'repository-col-input bg-dark text-white'

class TestParametersForm(forms.ModelForm):
    class Meta:
        model = TestParameters
        fields = ['param_name', 'parameters', 'version']

    def __init__(self, *args, **kwargs):
        super(TestParametersForm, self).__init__(*args, **kwargs)
        
        self.fields['version'].label = 'Python version'

        self.fields['param_name'].widget.attrs['class'] = 'hidden-field'
        self.fields['parameters'].widget.attrs['class'] = 'hidden-field'
        self.fields['version'].widget.attrs['class'] = 'hidden-field'

TestParametersFormSet = inlineformset_factory(Repository, TestParameters, form=TestParametersForm, extra=1)
