from django.contrib import admin
from .models import Contact
from contact.forms import ContactForm


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    form = ContactForm

