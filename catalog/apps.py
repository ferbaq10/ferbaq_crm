from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'
    verbose_name = "Catálogo"

    def ready(self):
        from .signals import register_catalog_signals
        register_catalog_signals()
