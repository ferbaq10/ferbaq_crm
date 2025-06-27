from django.apps import AppConfig


class ContactConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contact'
    verbose_name = "Contacto"

    def ready(self):
        from .signals import register_catalog_signals
        register_catalog_signals()
