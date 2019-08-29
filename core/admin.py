from django.contrib import admin
from .models import ClientModel, Clientele, Task
from .forms import PushTask

# admin.site.register(ClientModel)
admin.site.register(Clientele)
admin.site.register(Task)

class PersonAdmin(admin.ModelAdmin):
    form = PushTask
admin.site.register(ClientModel, PersonAdmin)
