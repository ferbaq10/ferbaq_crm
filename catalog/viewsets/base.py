from django.core.cache import cache
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class ListCacheMixin:
    """Mixin para cachear las respuestas del método list."""
    cache_timeout = 60 * 60  # 1 hora por defecto
    cache_prefix = "catalog"  # Prefijo para evitar colisiones

    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key()
        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"[Redis HIT] {cache_key}")
            return Response(cached_data)
        print(f"[Redis MISS] {cache_key}")

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=3600)
        return response

    def get_cache_key(self):
        return f"{self.cache_prefix}_{self.__class__.__name__}_list"

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.invalidate_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.invalidate_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.invalidate_cache()

    def invalidate_cache(self):
        cache_key = self.get_cache_key()
        cache.delete(cache_key)


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