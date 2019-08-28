from django import forms
from django.shortcuts import render
from .models import ClientModel, Clientele
from dal import autocomplete

class PushTask(forms.ModelForm):
    name = forms.ModelChoiceField(Clientele.objects.all())
    class Meta(object):
        """docstring for Meta."""
        model = ClientModel
        fields = ['name', 'reason', 'time_spent']
        widgets = {
            'name': autocomplete.ModelSelect2(url='name-autocomplete'),
        }
