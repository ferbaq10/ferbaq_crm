from django.contrib import admin
from .models import Opportunity, CommercialActivity
from .forms import OpportunityForm, CommercialActivityForm

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    form = OpportunityForm

@admin.register(CommercialActivity)
class CommercialActivityAdmin(admin.ModelAdmin):
    form = CommercialActivityForm
