from django.contrib import admin
from .models import Client
from .forms import ClientForm

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
