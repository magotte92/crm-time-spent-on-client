from django.urls import path
from django.conf.urls import url
from .views import RecordView, ClientAutocomplete
from .models import ClientModel
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('recorder/', RecordView.as_view(), name='recorder'),
    path('name-autocomplete/',
        ClientAutocomplete.as_view(model=ClientModel),
        name='name-autocomplete',
    ),

]
