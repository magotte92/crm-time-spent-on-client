from django.urls import path
from . import views

urlpatterns = [
    path('recorder/', views.manage_records, name='recorder'),
]
