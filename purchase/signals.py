from django.apps import apps
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from redis.exceptions import ConnectionError as RedisConnectionError
import logging

logger = logging.getLogger(__name__)

CATALOG_MODELS = ['PurchaseStatus']
APP_NAME = 'purchase'

def clear_list_cache_for(model_name, prefix="catalog"):
    try:
        cache_key = f"{prefix}_{model_name}ViewSet_list"
        print(f"🚨 Intentando invalidar cache: {cache_key}")
        cache.delete(cache_key)
        print(f"Cache invalidado: {cache_key}")
    except RedisConnectionError:
        logger.warning(f"Redis no disponible (clear cache signal): {model_name}")

def register_catalog_signals():
    for model_name in CATALOG_MODELS:
        model = apps.get_model(APP_NAME, model_name)

        def make_handler(model_name):
            def handler(sender, **kwargs):
                print(f"📌 Señal post_save/post_delete activada para {model_name}")
                print("Modelo ", model_name)
                clear_list_cache_for(model_name)
            return handler

        handler = make_handler(model_name)

        try:
            # Testea disponibilidad de Redis al momento de registrar señales
            cache.set("signal_test", "1", timeout=1)
            post_save.connect(handler, sender=model, weak=False)
            post_delete.connect(handler, sender=model, weak=False)
        except RedisConnectionError:
            logger.warning(f"Redis no disponible al registrar señales para {model_name}. Señales omitidas.")
