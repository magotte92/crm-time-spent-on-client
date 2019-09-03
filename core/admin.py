from django.contrib import admin
from .models import *
from .forms import PushTask

# admin.site.register(ClientModel)


class PersonAdmin(admin.ModelAdmin):
    form = PushTask


admin.site.register(ClientModel, PersonAdmin)
admin.site.register(Clientele)
admin.site.register(Task)
admin.site.register(SubTask)
