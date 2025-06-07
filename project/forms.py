from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        labels = {
            'description': 'Descripción',
            'latitude': 'Latitud',
            'longitude': 'Longitud',
            'project_status': 'Estatus del proyecto',
            'speciality': 'Especialidad',
            'subdivision': 'Subdivisión',
            'business_groups': 'Grupo empresarial',
            'work_cell': 'Célula de trabajo',
        }
        error_messages = {
            'latitude': {
                'invalid': 'Ingrese una latitud válida.',
            },
            'longitude': {
                'invalid': 'Ingrese una longitud válida.',
            },
        }

    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat is not None and (lat < -90 or lat > 90):
            raise forms.ValidationError("La latitud debe estar entre -90 y 90 grados.")
        return lat

    def clean_longitude(self):
        lon = self.cleaned_data.get('longitude')
        if lon is not None and (lon < -180 or lon > 180):
            raise forms.ValidationError("La longitud debe estar entre -180 y 180 grados.")
        return lon

    def clean_description(self):
        desc = self.cleaned_data.get('description')
        if desc and len(desc) < 10:
            raise forms.ValidationError("La descripción debe tener al menos 10 caracteres.")
        return desc
