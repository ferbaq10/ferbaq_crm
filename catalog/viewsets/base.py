import logging

from django.core.cache import cache
from redis.exceptions import ConnectionError as RedisConnectionError  # Import directo de redis-py
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

logger = logging.getLogger(__name__)

class ListCacheMixin:
    cache_timeout = 60 * 60  # 1 hora
    cache_prefix = "catalog"
    cache_enabled = True

    def list(self, request, *args, **kwargs):
        if not self.cache_enabled:
            return super().list(request, *args, **kwargs)

        cache_key = self.get_cache_key()
        cached_data = self._safe_cache_get(cache_key)

        if cached_data is not None:
            print(f"[Redis HIT] {cache_key}")
            return Response(cached_data)

        print(f"[Redis MISS] {cache_key}")
        response = super().list(request, *args, **kwargs)
        self._safe_cache_set(cache_key, response.data)
        return response

    def _safe_cache_get(self, key):
        try:
            return cache.get(key)
        except RedisConnectionError:
            logger.warning(f"Redis no disponible (get): clave '{key}'")
            return None

    def _safe_cache_set(self, key, data):
        try:
            cache.set(key, data, self.cache_timeout)
            logger.info(f"Cache SET: {key}")  # Para debugging
        except RedisConnectionError:
            logger.warning(f"Redis no disponible (set): clave '{key}'")

    def invalidate_cache(self):
        try:
            cache.delete(self.get_cache_key())
        except RedisConnectionError:
            logger.warning(f"Redis no disponible (delete): clave '{self.get_cache_key()}'")

    def get_cache_key(self):
        return f"{self.cache_prefix}_{self.__class__.__name__}_list"

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.invalidate_cache()


class AuthenticatedModelViewSet(ModelViewSet):
    """ViewSet base con autenticación requerida."""
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    model = None

    def get_queryset(self):
        optimized_getter = getattr(self, 'get_optimized_queryset', None)
        if callable(optimized_getter):
            return optimized_getter()

        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset

        assert self.model is not None, (
            f"{self.__class__.__name__} debe definir un atributo 'model'."
        )
        manager = getattr(self.model, 'all_objects', self.model.objects)
        return manager.all().order_by('-id')

    @action(detail=False, methods=['get'], url_path='actives')
    def actives(self, request):
        assert self.model is not None, (
            f"{self.__class__.__name__} debe definir un atributo 'model'."
        )
        manager = getattr(self.model, 'all_objects', self.model.objects)
        queryset = manager.filter(is_removed=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ¡ORDEN CORRECTO! Mixin primero, luego la clase base
class CachedViewSet(ListCacheMixin, AuthenticatedModelViewSet):
    """ViewSet base para catálogos con caché habilitado."""
    cache_timeout = 60 * 60 * 2  # 2 horas para catálogos