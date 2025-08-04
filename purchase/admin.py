from django.contrib import admin
from .models import PurchaseStatus
from .forms import PurchaseForm

@admin.register(PurchaseStatus)
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm
