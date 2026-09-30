from django.urls import path
from .views import PanelPageView

urlpatterns = [
    path('panel/', PanelPageView.as_view(), name='panel'),
]
