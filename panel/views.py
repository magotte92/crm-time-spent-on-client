from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import *
import pandas as pd


class PanelPageView(LoginRequiredMixin, TemplateView):
    template_name = 'panel.html'

    def get_context_data(self, **kwargs):
        context = super(PanelPageView, self).get_context_data(**kwargs)
        # qs = list(ClientModel.objects.values_list('name__name', 'task__task',
        #                                           'subtask__subtask', 'time_spent',
        #                                           'date_added',
        #                                           'dec_name').order_by(
        #                                           '-date_added'))
        qs = list(ClientModel.objects.values_list('name__name', 'task__task',
                                                  'subtask__subtask', 'time_spent'))
        df = pd.DataFrame(qs, columns=['name', 'task', 'subtask', 'time_spent'])
        df.to_csv('./media/recent.csv', sep=';', index=None)
        df = pd.read_csv('./media/recent.csv', sep=';')
        df = df.groupby(['name', 'task', 'subtask']).sum().sum(level=['name', 'task', 'subtask']).fillna(0).reset_index()
        df['time_spent'] = pd.to_datetime(df.time_spent, unit='m').dt.strftime('%H:%M')
        df = df.sort_values(by=['name', 'time_spent'])
        context.update({'df': df.values})
        return context
