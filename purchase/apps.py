from django.apps import AppConfig

from core.utils.signals import should_skip_signal_registration


class PurchaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchase'

    def ready(self):
        if should_skip_signal_registration():
            return

        try:
            from . import signals
            signals.register_catalog_signals()
        except Exception as e:
            print(f"❌ Error registrando purchase signals: {e}")
