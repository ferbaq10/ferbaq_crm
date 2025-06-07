from django.contrib import admin
from .models import (
    UDN, WorkCell, BusinessGroup, Division, Subdivision,
    Speciality, ProjectStatus, City, Period, StatusOpportunity
)
from .forms import (
    UDNForm, WorkCellForm, BusinessGroupForm, DivisionForm, SubdivisionForm,
    SpecialityForm, ProjectStatusForm, CityForm, PeriodForm, StatusOpportunityForm
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

@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    form = SpecialityForm

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
