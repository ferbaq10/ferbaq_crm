from django import forms
from .models import Opportunity, CommercialActivity
from django.core.validators import validate_email

class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = '__all__'
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
            'amount': 'Monto',
            'status_opportunity': 'Estado de la oportunidad',
            'contact': 'Contacto',
            'city': 'Ciudad'
        }
        error_messages = {
            'name': {
                'required': 'Este campo es obligatorio.',
                'unique': 'Ya existe una oportunidad con este nombre.'
            },
            'email': {
                'unique': 'Ya existe una oportunidad con este correo.',
                'invalid': 'Ingrese un correo válido.'
            },
            'amount': {
                'invalid': 'El monto debe ser un número válido.'
            },
            'phone': {
                'invalid': 'El teléfono debe ser numérico.'
            }
        }


class ComercialActivityForm(forms.ModelForm):
    class Meta:
        model = CommercialActivity
        fields = '__all__'
        labels = {
            'name': 'Nombre',
            'oportunity_id': 'Oportunidad'
        }
        error_messages = {
            'name': {
                'required': 'Este campo es obligatorio.',
                'unique': 'Ya existe una actividad con este nombre.'
            }
        }