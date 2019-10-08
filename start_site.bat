@echo off
E:
cd E:\git-projects\crm-time-spent-on-client
cmd /k "cd C:\crm-time-spent-on-client & pipenv run manage.py runserver 0.0.0.0:8000"
