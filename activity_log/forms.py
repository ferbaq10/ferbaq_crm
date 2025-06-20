from django import forms
from .models import ActivityLog

class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['name', 'latitude', 'longitude', 'opportunity']

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre del registro'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Latitud'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Longitud'}),
            'opportunity': forms.Select(attrs={'placeholder': 'Selecciona una oportunidad'}),
        }

        error_messages = {
            'name': {
                'required': 'El nombre es obligatorio.',
                'unique': 'Este nombre ya ha sido registrado.',
                'max_length': 'El nombre no puede superar los 100 caracteres.',
            },
            'latitude': {
                'invalid': 'Ingresa una latitud válida.',
            },
            'longitude': {
                'invalid': 'Ingresa una longitud válida.',
            },
            'opportunity': {
                'invalid_choice': 'Selecciona una oportunidad válida.',
            },
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("El nombre no puede estar vacío.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get("latitude")
        lng = cleaned_data.get("longitude")

        # Validación personalizada: si hay latitud debe haber longitud (y viceversa)
        if (lat and not lng) or (lng and not lat):
            raise forms.ValidationError("Si proporcionas latitud, también debes proporcionar longitud, y viceversa.")

        return cleaned_data
