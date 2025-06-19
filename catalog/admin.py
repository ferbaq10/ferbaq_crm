from django.contrib import admin
from .models import (
    UDN, WorkCell, BusinessGroup, Division, Subdivision,
    Specialty, ProjectStatus, City, Period, StatusOpportunity, Currency, Job, OpportunityType
)
from .forms import (
    UDNForm, WorkCellForm, BusinessGroupForm, DivisionForm, SubdivisionForm,
    SpecialtyForm, ProjectStatusForm, CityForm, PeriodForm, StatusOpportunityForm, CurrencyForm,
    JobForm, OpportunityTypeForm
)

@admin.register(UDN)
class UDNAdmin(admin.ModelAdmin):
    form = UDNForm

@admin.register(WorkCell)
class WorkCellAdmin(admin.ModelAdmin):
    form = WorkCellForm

@admin.register(BusinessGroup)
class BusinessGroupAdmin(admin.ModelAdmin):
    form = BusinessGroupForm

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    form = DivisionForm

@admin.register(Subdivision)
class SubdivisionAdmin(admin.ModelAdmin):
    form = SubdivisionForm

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    form = SpecialtyForm

@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    form = ProjectStatusForm

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityForm

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    form = PeriodForm

@admin.register(StatusOpportunity)
class StatusOpportunityAdmin(admin.ModelAdmin):
    form = StatusOpportunityForm


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    form = JobForm

@admin.register(Job)
class CurrencyAdmin(admin.ModelAdmin):
    form = CurrencyForm


@admin.register(OpportunityType)
class OpportunityTypeAdmin(admin.ModelAdmin):
    form = OpportunityTypeForm
