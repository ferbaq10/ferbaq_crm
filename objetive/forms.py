from django import forms
from objetive.models import Objetive

class ObjetiveForm(forms.ModelForm):
    class Meta:
        model = Objetive
        fields = '__all__'
        error_messages = {
            'name': {
                'unique': "Este nombre de objetivo ya existe.",
                'max_length': "El nombre no puede exceder 100 caracteres.",
                'required': "El nombre del objetivo es obligatorio."
            },
            'amount': {
                'required': "El monto es obligatorio.",
                'invalid': "El monto debe ser un número decimal válido."
            },
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("El nombre es obligatorio.")
        return name

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise forms.ValidationError("El monto es obligatorio.")
        if amount < 0:
            raise forms.ValidationError("El monto no puede ser negativo.")
        return amount
