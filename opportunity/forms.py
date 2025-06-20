from django import forms
from opportunity.models import Opportunity, CommercialActivity


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            'name', 'description', 'amount', 'number_fvt',
            'date_reception', 'sent_date',
            'status_opportunity', 'contact', 'currency',
            'commercial_activity', 'agent', 'project', 'opportunityType'
        ]
        error_messages = {
            'name': {
                'unique': 'Ya existe una oportunidad con este nombre.',
                'required': 'El nombre es obligatorio.',
            },
            'amount': {
                'required': 'El monto es obligatorio.',
                'invalid': 'Debe ser un número válido.',
            },
            'number_fvt': {
                'unique': 'Este formato de venta ya está registrado.',
                'required': 'El formato de venta es obligatorio.',
            },
            'date_reception': {'required': 'La fecha de recepción es obligatoria.'},
            'status_opportunity': {'required': 'El estado es obligatorio.'},
            'contact': {'required': 'El contacto es obligatorio.'},
            'currency': {'required': 'La moneda es obligatoria.'},
            'agent': {'required': 'El usuario asignado es obligatorio.'},
            'project': {'required': 'El proyecto es obligatorio.'},
            'opportunityType': {'required': 'El tipo de oportunidad es obligatorio.'},
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("El monto debe ser mayor a cero.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        date_reception = cleaned_data.get('date_reception')
        sent_date = cleaned_data.get('sent_date')
        if date_reception and sent_date and sent_date < date_reception:
            raise forms.ValidationError("La fecha de envío no puede ser anterior a la de recepción.")


class CommercialActivityForm(forms.ModelForm):
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
