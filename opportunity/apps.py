from django.apps import AppConfig

from core.utils.signals import should_skip_signal_registration


class OpportunityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'opportunity'
    verbose_name = "Oportunidad"

    def ready(self):
        if should_skip_signal_registration():
            return

        try:
            from .signals import register_catalog_signals
            register_catalog_signals()
        except Exception as e:
            import traceback
            traceback.print_exc()