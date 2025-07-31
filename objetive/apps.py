from django.apps import AppConfig

from core.utils.signals import should_skip_signal_registration


class ObjetiveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'objetive'
    verbose_name = "Ojetivo"

    def ready(self):
        if should_skip_signal_registration():
            return

        from .signals import register_catalog_signals
        register_catalog_signals()
