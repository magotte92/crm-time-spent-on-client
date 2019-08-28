from django.urls import path
from django.conf.urls import url
from .views import RecordView, ClientAutocomplete
from .models import ClientModel

urlpatterns = [
    path('recorder/', RecordView.as_view(), name='recorder'),
    url(r'/name-autocomplete/$',
        ClientAutocomplete.as_view(model=ClientModel),
        name='name-autocomplete',
    ),
]
