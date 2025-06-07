from django.contrib import admin
from .models import Objetive
from .forms import ObjetiveForm

@admin.register(Objetive)
class Objetivedmin(admin.ModelAdmin):
    form = ObjetiveForm
