from django.apps import AppConfig


class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project'
    verbose_name = "Proyecto"

    def ready(self):
        from .signals import register_catalog_signals
        register_catalog_signals()
