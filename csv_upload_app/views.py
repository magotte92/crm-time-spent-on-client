from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from core.models import Clientele
import csv
import io

@permission_required('admin.can_add_log_entry')
def clientele_upload(request, **kwargs):
    template = 'csv_upload.html'
    prompt = {
        'order': 'Ανανέβασμά πελατών'
        }

    if request.method == 'GET':
        return render(request, template, prompt)

    csv_file = request.FILES['file']

    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'This is not a csv File!')

    data_set = csv_file.read().decode('1253')
    io_string = io.StringIO(data_set)
    next(io_string)
    for col in csv.reader(io_string, delimiter=';', quotechar='|'):
        _, created = Clientele.objects.update_or_create(
            Aa=int(col[0]),
            name=col[1],
            )
    context = {}
    return render(request, template, context)
