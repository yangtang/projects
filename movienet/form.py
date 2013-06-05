__author__ = 'ytang'

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from datetime import date

year = date.today().year
BIRTH_YEAR_CHOICES = range(year-100,year+1)
GENDER_CHOICES = (('M','male'),('F','female'))

class RegisterForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    birthday = forms.DateField(widget=SelectDateWidget(years=BIRTH_YEAR_CHOICES))
    gender = forms.ChoiceField(widget=RadioSelect, choices=GENDER_CHOICES)
    email = forms.EmailField()
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=32, widget=forms.PasswordInput)

    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
             raise forms.ValidationError("Passwords don't match")

        return self.cleaned_data


class LogInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)


