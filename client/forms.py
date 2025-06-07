from django import forms
from client.models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        error_messages = {
            'rfc': {
                'unique': "Este RFC ya está registrado.",
                'max_length': "El RFC no puede exceder 20 caracteres.",
                'required': "El campo RFC es obligatorio."
            },
            'company': {
                'unique': "Esta razón social ya está registrada.",
                'max_length': "La razón social no puede exceder 100 caracteres.",
                'required': "El campo razón social es obligatorio."
            },
        }

    def clean_rfc(self):
        rfc = self.cleaned_data.get('rfc')
        if not rfc:
            raise forms.ValidationError("El RFC es obligatorio.")
        return rfc

    def clean_company(self):
        company = self.cleaned_data.get('company')
        if not company:
            raise forms.ValidationError("La razón social es obligatoria.")
        return company
