from django import forms
from objetive.models import Objetive


class ObjetiveForm(forms.ModelForm):
    class Meta:
        model = Objetive
        fields = ['name', 'amount', 'currency', 'period', 'user']
        error_messages = {
            'name': {
                'required': 'El nombre es obligatorio.',
                'unique': 'Este nombre de objetivo ya existe.',
                'max_length': 'El nombre no puede exceder 100 caracteres.'
            },
            'amount': {
                'required': 'El monto es obligatorio.',
                'invalid': 'Debe ser un número válido.'
            },
            'currency': {
                'invalid': 'Debe seleccionar una moneda válida.'
            },
            'period': {
                'invalid': 'Debe seleccionar un período válido.'
            },
            'user': {
                'invalid': 'Debe seleccionar un usuario válido.'
            }
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount < 0:
            raise forms.ValidationError("El monto debe ser mayor o igual a cero.")
        return amount
