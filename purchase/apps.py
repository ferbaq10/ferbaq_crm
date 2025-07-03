from django.apps import AppConfig


class PurchaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchase'

    def ready(self):
        try:
            from . import signals
            signals.register_catalog_signals()
            print("✅ Purchase signals registradas correctamente")
        except Exception as e:
            print(f"❌ Error registrando purchase signals: {e}")
