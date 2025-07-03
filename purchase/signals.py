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
        possible_prefixes = ["catalog", "purchase", ""]
        possible_suffixes = ["ViewSet_list", "_list", ""]

        cache_keys_to_try = []

        for pref in possible_prefixes:
            for suff in possible_suffixes:
                if pref and suff:
                    cache_keys_to_try.append(f"{pref}_{model_name}{suff}")
                elif pref:
                    cache_keys_to_try.append(f"{pref}_{model_name}")
                elif suff:
                    cache_keys_to_try.append(f"{model_name}{suff}")
                else:
                    cache_keys_to_try.append(model_name)

        cache_keys_to_try.extend([
            "catalog_PurchaseViewSet_list",
            "purchase_PurchaseViewSet_list",
            "PurchaseViewSet_list",
            "purchases_list",
        ])

        cache.clear()
        print("🗑️ TODO EL CACHE INVALIDADO POR SIGNAL")

        for cache_key in cache_keys_to_try:
            cache.delete(cache_key)
            print(f"🗑️ Cache invalidado por signal: {cache_key}")

    except RedisConnectionError:
        logger.warning(f"Redis no disponible (clear cache signal): {model_name}")
    except Exception as e:
        logger.warning(f"Error en signal invalidando caché: {e}")
        print(f"⚠️ Error en signal: {e}")


def register_catalog_signals():
    for model_name in CATALOG_MODELS:
        try:
            model = apps.get_model(APP_NAME, model_name)

            def make_handler(model_name):
                def handler(sender, **kwargs):
                    print(f"📌 SIGNAL ACTIVADA: post_save/post_delete para {model_name}")
                    print(f"📌 Sender: {sender}")
                    print(f"📌 Instance: {kwargs.get('instance')}")
                    clear_list_cache_for(model_name)

                return handler

            handler = make_handler(model_name)

            cache.set("signal_test", "1", timeout=1)
            post_save.connect(handler, sender=model, weak=False)
            post_delete.connect(handler, sender=model, weak=False)
            print(f"✅ Signals registradas exitosamente para {model_name}")

        except RedisConnectionError:
            logger.warning(f"Redis no disponible al registrar señales para {model_name}. Señales omitidas.")
        except Exception as e:
            logger.error(f"Error registrando signals para {model_name}: {e}")
            print(f"❌ Error registrando signals: {e}")