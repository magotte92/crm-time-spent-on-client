from django.forms import ModelForm
from django.shortcuts import render
from .models import ClientModel
from django.forms.models import modelformset_factory

class PushTask(ModelForm):

    class Meta(object):
        """docstring for Meta."""
        model = ClientModel
        fields = ['name', 'reason', 'time_spent']


PushTaskFormSet = modelformset_factory(ClientModel, form=PushTask)
