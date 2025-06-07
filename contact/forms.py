# contact/forms.py

from django import forms
from contact.models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'
        error_messages = {
            'name': {
                'required': "El campo nombre es obligatorio.",
                'max_length': "El nombre no puede tener más de 100 caracteres.",
                'unique': "Este nombre de contacto ya existe.",
            },
            'address': {
                'max_length': "La dirección no puede tener más de 255 caracteres.",
            },
            'email': {
                'required': "El campo correo electrónico es obligatorio.",
                'invalid': "Debe ingresar un correo electrónico válido.",
                'max_length': "El correo no puede tener más de 100 caracteres.",
                'unique': "Este correo ya ha sido registrado.",
            },
            'phone': {
                'invalid': "El número debe contener al menos 10 dígitos numéricos.",
                'max_length': "El número de teléfono no puede tener más de 15 caracteres.",
            },
            'city_id': {
                'required': "Debe seleccionar una ciudad.",
                'invalid_choice': "La ciudad seleccionada no es válida.",
            },
        }
