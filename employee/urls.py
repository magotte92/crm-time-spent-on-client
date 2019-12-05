from django.urls import path
from django.conf.urls import url
from .views import AllClientsPageView, EmployeeTabPageView, SumOfClientView, AllEmployeesPage, AllTaskPage, AntonPage, TimeBasedPage, ExportAllPageView
from django.contrib.auth.decorators import permission_required


urlpatterns = [
    path('', permission_required('is_staff')(AntonPage.as_view()), name='anton'),
    path('all_clients/', permission_required('is_staff')(AllClientsPageView.as_view()), name='all_clients'),
    path('employees/', permission_required('is_staff')(EmployeeTabPageView.as_view()), name='employees'),
    path('client_sum/', permission_required('is_staff')(SumOfClientView.as_view()), name='client_sum'),
    # path('all_employees/', permission_required('is_staff')(AllEmployeesPage.as_view()), name='all_employees'),
    path('all_tasks/', permission_required('is_staff')(AllTaskPage.as_view()), name='all_tasks'),
    path('timer/', permission_required('is_staff')(TimeBasedPage.as_view()), name='timer'),
    path('anton_export/', permission_required('is_staff')(ExportAllPageView.as_view()), name='exporter'),
]
