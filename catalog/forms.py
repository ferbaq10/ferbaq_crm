from django import forms
from catalog.models import (
    UDN, WorkCell, BusinessGroup, Division, Subdivision,
    Speciality, ProjectStatus, City, Period, StatusOpportunity
)

class UDNForm(forms.ModelForm):
    class Meta:
        model = UDN
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El nombre de la UDN es obligatorio.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'unique': "Este nombre de UDN ya existe.",
            }
        }

class WorkCellForm(forms.ModelForm):
    class Meta:
        model = WorkCell
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El nombre de la célula de trabajo es obligatorio.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'unique': "Este nombre de célula de trabajo ya existe.",
            }
        }

class BusinessGroupForm(forms.ModelForm):
    class Meta:
        model = BusinessGroup
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El nombre del grupo empresarial es obligatorio.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'unique': "Este grupo empresarial ya existe.",
            }
        }

class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El nombre de la división es obligatorio.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'unique': "Esta división ya existe.",
            }
        }

class SubdivisionForm(forms.ModelForm):
    class Meta:
        model = Subdivision
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El nombre de la subdivisión es obligatorio.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'unique': "Esta subdivisión ya existe.",
            }
        }

class SpecialityForm(forms.ModelForm):
    class Meta:
        model = Speciality
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El nombre de la especialidad es obligatorio.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'unique': "Esta especialidad ya existe.",
            }
        }

class ProjectStatusForm(forms.ModelForm):
    class Meta:
        model = ProjectStatus
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El nombre del estatus es obligatorio.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'unique': "Este estatus ya existe.",
            }
        }

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El nombre de la ciudad es obligatorio.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'unique': "Esta ciudad ya existe.",
            }
        }

class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El nombre del período es obligatorio.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'unique': "Este período ya existe.",
            }
        }

class StatusOpportunityForm(forms.ModelForm):
    class Meta:
        model = StatusOpportunity
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El nombre del estatus de oportunidad es obligatorio.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'unique': "Este estatus de oportunidad ya existe.",
            }
        }
