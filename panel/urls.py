from django.urls import path
from django.conf.urls import url
from .views import PanelPageView

urlpatterns = [
    path('panel/', PanelPageView.as_view(), name='panel'),
]
