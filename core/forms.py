from django import forms
from django.shortcuts import render
from .models import *
from dal import autocomplete
from .fields import GroupedModelChoiceField


class PushTask(forms.ModelForm):
    # name = forms.ModelChoiceField(Clientele.objects.all())
    subtask = GroupedModelChoiceField(
        queryset=SubTask.objects.exclude(mother_task=None),
        choices_groupby='mother_task'
    )
    class Meta(object):
        """docstring for Meta."""
        model = ClientModel
        fields = ['name', 'subtask', 'time_spent']
        widgets = {
            'name': autocomplete.ModelSelect2(url='name-autocomplete'),
        }
