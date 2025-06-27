from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet

import logging
from django.core.cache import cache
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class ListCacheMixin:
    """
    Mixin para cachear las respuestas del metodo list con fallback seguro.
    Si Redis no está disponible, funciona normalmente sin cache.
    """
    cache_timeout = 60 * 60  # 1 hora por defecto
    cache_prefix = "catalog"  # Prefijo para evitar colisiones
    cache_enabled = True  # Permite deshabilitar cache si es necesario

    def list(self, request, *args, **kwargs):
        # Si el cache está deshabilitado, ir directamente a la DB
        if not self.cache_enabled:
            return super().list(request, *args, **kwargs)

        # Intentar usar cache con manejo de errores
        cache_key = self.get_cache_key()
        cached_data = self._safe_cache_get(cache_key)

        if cached_data is not None:
            print(f"[Redis HIT] {cache_key}")
            return Response(cached_data)

        print(f"[Redis MISS] {cache_key}")

        # Obtener datos de la base de datos
        response = super().list(request, *args, **kwargs)

        # Intentar guardar en cache (sin fallar si Redis no está disponible)
        self._safe_cache_set(cache_key, response.data)

        return response

    def get_cache_key(self):
        """Genera la clave de cache única para este viewset."""
        return f"{self.cache_prefix}_{self.__class__.__name__}_list"

    def perform_create(self, serializer):
        """Invalidar cache después de crear un registro."""
        super().perform_create(serializer)
        self.invalidate_cache()

    def perform_update(self, serializer):
        """Invalidar cache después de actualizar un registro."""
        super().perform_update(serializer)
        self.invalidate_cache()

    def perform_destroy(self, instance):
        """Invalidar cache después de eliminar un registro."""
        super().perform_destroy(instance)
        self.invalidate_cache()

    def invalidate_cache(self):
        """Invalidar cache de forma segura."""
        if not self.cache_enabled:
            return

        cache_key = self.get_cache_key()
        success = self._safe_cache_delete(cache_key)

        if success:
            print(f"[Redis INVALIDATED] {cache_key}")
        else:
            print(f"[Redis INVALIDATION FAILED] {cache_key}")

    def _safe_cache_get(self, cache_key):
        """
        Obtener datos del cache de forma segura.
        Retorna None si hay error o no hay datos.
        """
        try:
            return cache.get(cache_key)
        except Exception as e:
            logger.warning(f"Error al obtener cache {cache_key}: {e}")
            print(f"[Redis ERROR] No se pudo obtener {cache_key}: {str(e)}")
            return None

    def _safe_cache_set(self, cache_key, data):
        """
        Guardar datos en cache de forma segura.
        No falla si Redis no está disponible.
        """
        try:
            cache.set(cache_key, data, timeout=self.cache_timeout)
            print(f"[Redis CACHED] {cache_key}")
            return True
        except Exception as e:
            logger.warning(f"Error al guardar cache {cache_key}: {e}")
            print(f"[Redis ERROR] No se pudo cachear {cache_key}: {str(e)}")
            return False

    def _safe_cache_delete(self, cache_key):
        """
        Eliminar datos del cache de forma segura.
        No falla si Redis no está disponible.
        """
        try:
            cache.delete(cache_key)
            return True
        except Exception as e:
            logger.warning(f"Error al invalidar cache {cache_key}: {e}")
            print(f"[Redis ERROR] No se pudo invalidar {cache_key}: {str(e)}")
            return False

    @classmethod
    def disable_cache(cls):
        """Método para deshabilitar cache globalmente en esta clase."""
        cls.cache_enabled = False
        print("[Redis] Cache deshabilitado para esta clase")

    @classmethod
    def enable_cache(cls):
        """Método para habilitar cache globalmente en esta clase."""
        cls.cache_enabled = True
        print("[Redis] Cache habilitado para esta clase")


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