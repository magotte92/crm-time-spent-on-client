from django.shortcuts import render
from .forms import PushTaskFormSet
from django.shortcuts import render_to_response


def manage_records(request):

    if request.method == 'POST':
        formset = PushTaskFormSet(request.POST)
        if formset.is_valid():
            # do something with the formset.cleaned_data
            formset.save(commit=False)
            formset.dec_name = request.user
            formset.save()

            return render(request, 'manage_records.html')
    else:
        formset = PushTaskFormSet()
    return render(request, 'manage_records.html', {'formset': formset})
