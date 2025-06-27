from django.apps import AppConfig


class ObjetiveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'objetive'
    verbose_name = "Ojetivo"

    def ready(self):
        from .signals import register_catalog_signals
        register_catalog_signals()
