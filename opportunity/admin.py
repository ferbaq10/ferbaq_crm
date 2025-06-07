from django.contrib import admin
from .models import Opportunity, ComercialActivity
from .forms import OpportunityForm, ComercialActivityForm

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    form = OpportunityForm

@admin.register(ComercialActivity)
class ComercialActivityAdmin(admin.ModelAdmin):
    form = ComercialActivityForm
