from django.urls import path
from django.conf.urls import url
from .views import clientele_upload

urlpatterns = [
    path('magotte/csv_upload_app/', clientele_upload, name='csv_upload_app'),
]
