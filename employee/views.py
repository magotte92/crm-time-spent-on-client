from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
import pandas as pd
from core.models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import datetime

def make_all_client():
    qs = list(ClientModel.objects.values_list('name__name', 'task__task', 'subtask__subtask', 'time_spent'))
    df = pd.DataFrame(qs, columns=['name', 'task', 'subtask', 'time_spent'])
    df.to_csv('stuff/all.csv', sep=';', index=None)


class AllClientsPageView(TemplateView):
    template_name = 'all_clients.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AllClientsPageView, self).get_context_data(**kwargs)

        make_all_client()
        all_clients = pd.read_csv('stuff/all.csv', sep=';')
        all_clients = all_clients.groupby(['name', 'task', 'subtask']).sum().sum(level=['name', 'task', 'subtask']).fillna(0).reset_index()
        all_clients['time_spent'] = pd.to_timedelta(all_clients.time_spent, unit='m')

        context.update({'df': all_clients.values})
        return context

def make_all_employee():
    qs = list(ClientModel.objects.values_list('dec_name',
                                              'time_spent', 'date_added'))
    df = pd.DataFrame(qs, columns=['dec_name',
                                   'time_spent', 'date_added'])

    df.date_added = df.date_added.values.astype('M8[D]')

    df.to_csv('stuff/employees.csv', sep=';', index=None)


class EmployeeTabPageView(TemplateView):
    template_name = 'employee_tab.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EmployeeTabPageView, self).get_context_data(**kwargs)

        make_all_employee()
        employees = pd.read_csv('stuff/employees.csv', sep=';')

        employees = pd.read_csv('stuff/employees.csv', sep=';')
        employees = employees.groupby(['dec_name', 'date_added']).sum().sum(level=['dec_name', 'date_added']).fillna(0).reset_index()
        employees['time_spent'] = pd.to_datetime(employees.time_spent, unit='m').dt.strftime('%H:%M')
        context.update({'df': employees.values})
        
        return context


class SumOfClientView(TemplateView):
    template_name = 'clientsum.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SumOfClientView, self).get_context_data(**kwargs)
        make_all_client()
        all_clients = pd.read_csv('stuff/all.csv', sep=';')

        all_clients = all_clients.drop(columns=['task', 'subtask'])
        all_clients = all_clients.groupby(['name']).sum().sum(level=['name']).fillna(0).reset_index()
        all_clients['time_spent'] = pd.to_timedelta(all_clients.time_spent, unit='m')
        all_clients = all_clients.sort_values(by='time_spent', ascending=False)
        
        context.update({'df': all_clients.values})
        return context


def make_all_employees():
    qs = list(ClientModel.objects.values_list('task__task', 'subtask__subtask', 'time_spent'))
    df = pd.DataFrame(qs, columns=['name', 'task', 'subtask', 'time_spent'])
    df.to_csv('stuff/all_employees.csv', sep=';', index=None)


class AllEmployeesPage(TemplateView):
    template_name = 'all_employees.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AllEmployeesPage, self).get_context_data(**kwargs)

        make_all_employees()
        all_clients = pd.read_csv('stuff/all_employees.csv', sep=';')
        
        all_clients = all_clients.groupby(['name', 'task', 'subtask']).sum().sum(level=['name', 'task', 'subtask']).fillna(0).reset_index()
        all_clients['time_spent'] = pd.to_timedelta(all_clients.time_spent, unit='m')

        context.update({'df': all_clients.values})
        return context



class AllTaskPage(TemplateView):
    template_name = 'all_tasks.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AllTaskPage, self).get_context_data(**kwargs)

        make_all_client()
        synolo = pd.DataFrame()
        all_clients = pd.read_csv('stuff/all.csv', sep=';')
        all_clients = all_clients.drop(columns=['name'])
        summarize = all_clients.groupby(['task', 'subtask']).sum().sum(level=['task', 'subtask']).fillna(0).reset_index()
        averize = all_clients.groupby(['task', 'subtask']).mean().mean(level=['task', 'subtask']).fillna(0).reset_index()
        minimize = all_clients.groupby(['task', 'subtask']).min().min(level=['task', 'subtask']).fillna(0).reset_index()
        maximize = all_clients.groupby(['task', 'subtask']).max().max(level=['task', 'subtask']).fillna(0).reset_index()
        
        synolo['task'] = summarize['task']
        synolo['subtask'] = summarize['subtask']
        synolo['summarize'] = pd.to_timedelta(summarize.time_spent, unit='m')
        synolo['averize'] = pd.to_datetime(averize.time_spent, unit='m').dt.strftime('%H:%M')
        synolo['minimize'] = pd.to_datetime(minimize.time_spent, unit='m').dt.strftime('%H:%M')
        synolo['maximize'] = pd.to_datetime(maximize.time_spent, unit='m').dt.strftime('%H:%M')
        synolo = synolo.drop(columns='summarize')
        synolo = synolo.sort_values(by='task', ascending=False)
        context.update({'df': synolo.values})
        return context