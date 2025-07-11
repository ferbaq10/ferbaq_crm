import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class CacheInvalidationMixin:
    """
    Mixin reutilizable para serializers que quieran invalidar cache de manera uniforme.
    """

    cache_keys = []  # Sobrescribe esta lista en cada serializer

    @classmethod
    def is_redis_available(cls):
        try:
            backend = settings.CACHES.get('default', {}).get('BACKEND', '')
            if 'redis' not in backend.lower():
                return False
            cache.set("redis_test_key", "ok", 1)
            return cache.get("redis_test_key") == "ok"
        except Exception as e:
            logger.debug(f"Redis no disponible: {e}")
            return False

    @classmethod
    def invalidate_caches(cls):
        if not cls.is_redis_available():
            logger.debug(f"{cls.__name__}: Redis no disponible para invalidación de cache.")
            return

        try:
            if cls.cache_keys:
                cache.delete_many(cls.cache_keys)
                logger.info(f"{cls.__name__}: Cache invalidado para {cls.cache_keys}")
            else:
                logger.debug(f"{cls.__name__}: No hay claves para invalidar.")
        except Exception as e:
            logger.warning(f"{cls.__name__}: Error invalidando caches: {e}")
