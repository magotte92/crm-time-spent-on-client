from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.generic import View
from .forms import PushTask
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from dal import autocomplete
from django.contrib.auth import logout
import json
from django.http import HttpResponse


class ClientAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Clientele.objects.none()

        # qs = Clientele.objects.values_list('name', flat=True)
        qs = Clientele.objects.all().order_by('name')
        if self.q:
            qs = qs.filter(name__istartswith=self.q.upper()).order_by('-name')

        return qs


class RecordView(LoginRequiredMixin, View):
    template_name = 'manage_records.html'
    username = ''

    def get(self, request):
        form = PushTask()
        return render(request, self.template_name, {'form': form})


    def post(self, request):

        if request.user.is_authenticated:
            form = PushTask(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                # profile.ip_address = request.META['REMOTE_ADDR']
                profile.dec_name = request.user
                profile.task = profile.subtask.mother_task
                profile.save()
                return redirect('recorder')
            print('Prob Not')
            args = {'form': form}

            return render(request, self.template_name, {'form': form})
