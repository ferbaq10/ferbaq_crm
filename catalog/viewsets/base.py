import logging

from django.db.models import QuerySet
from redis.exceptions import ConnectionError as RedisConnectionError  # Import directo de redis-py
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet

logger = logging.getLogger(__name__)

import logging
from django.core.cache import cache
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


class ListCacheMixin:
    cache_timeout = 60 * 60  # 1 hora
    cache_prefix = "catalog"
    cache_enabled = True

    def list(self, request, *args, **kwargs):
        model = getattr(self, "model", None)
        if model is not None:
            codename = f"{model._meta.app_label}.view_{model._meta.model_name}"
            if not request.user.has_perm(codename):
                raise PermissionDenied(f"No tienes permiso")

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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create genérico con invalidaciones automáticas"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Crear instancia
        instance = serializer.save()

        # Obtener instancia optimizada (si el ViewSet define este método)
        if hasattr(self, 'get_optimized_instance'):
            instance = self.get_optimized_instance(instance.pk)

        # Invalidaciones automáticas
        self._perform_cache_invalidations('create', instance)

        # Serializar respuesta
        read_serializer_class = getattr(self, 'read_serializer_class', self.get_serializer_class())
        read_serializer = read_serializer_class(instance)

        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Update genérico con invalidaciones automáticas"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Actualizar instancia
        updated_instance = serializer.save()

        # Obtener instancia optimizada (si el ViewSet define este método)
        if hasattr(self, 'get_optimized_instance'):
            updated_instance = self.get_optimized_instance(updated_instance.pk)

        # Invalidaciones automáticas
        self._perform_cache_invalidations('update', updated_instance)

        # Serializar respuesta
        read_serializer_class = getattr(self, 'read_serializer_class', self.get_serializer_class())
        read_serializer = read_serializer_class(updated_instance)

        return Response(read_serializer.data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """Destroy genérico con invalidaciones automáticas"""
        instance = self.get_object()
        instance_id = instance.pk

        # Eliminar instancia
        instance.delete()

        # Invalidaciones automáticas
        self._perform_cache_invalidations('destroy', None, instance_id=instance_id)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _perform_cache_invalidations(self, action, instance=None, instance_id=None):
        """
        Invalidaciones automáticas basadas en configuración del ViewSet
        """
        # 1. Invalidar cache principal del listado
        self.invalidate_cache()

        # 2. Invalidar cache de detalle si aplica
        if instance_id or (instance and hasattr(instance, 'pk')):
            detail_id = instance_id or instance.pk
            self._invalidate_detail_cache(detail_id)

        # 3. Invalidar caches del serializer (si tiene el método)
        write_serializer_class = getattr(self, 'write_serializer_class', None)
        if write_serializer_class and hasattr(write_serializer_class, 'invalidate_caches'):
            write_serializer_class.invalidate_caches()

        # 4. Invalidar caches relacionados específicos (si el ViewSet los define)
        if hasattr(self, 'get_related_cache_keys'):
            related_keys = self.get_related_cache_keys(action, instance)
            self._invalidate_related_caches(related_keys)

        # 5. Hook para invalidaciones personalizadas
        if hasattr(self, 'perform_additional_cache_invalidations'):
            self.perform_additional_cache_invalidations(action, instance, instance_id)

    def _invalidate_detail_cache(self, detail_id):
        """Invalidar cache de detalle específico"""
        cache_key = f"{self.cache_prefix}_detail_{detail_id}"
        try:
            cache.delete(cache_key)
            logger.info(f"Cache invalidado: {cache_key}")
        except Exception as e:
            logger.warning(f"Error invalidando cache de detalle: {e}")

    def _invalidate_related_caches(self, cache_keys):
        """Invalidar lista de caches relacionados"""
        if not cache_keys:
            return

        try:
            deleted_count = 0
            for key in cache_keys:
                try:
                    if cache.delete(key):
                        deleted_count += 1
                except Exception as key_error:
                    logger.warning(f"Error invalidando cache específico {key}: {key_error}")

            logger.info(f"Invalidados {deleted_count}/{len(cache_keys)} caches relacionados")

        except Exception as e:
            logger.warning(f"Error invalidando caches relacionados: {e}")

    def _safe_cache_get(self, key):
        try:
            return cache.get(key)
        except RedisConnectionError:
            logger.warning(f"Redis no disponible (get): clave '{key}'")
            return None

    def _safe_cache_set(self, key, data, timeout=None):
        if timeout is None:
            timeout = self.cache_timeout

        try:
            cache.set(key, data, timeout)
            logger.info(f"Cache SET: {key}")
        except RedisConnectionError:
            logger.warning(f"Redis no disponible (set): clave '{key}'")

    def invalidate_cache(self):
        try:
            cache.delete(self.get_cache_key())
        except RedisConnectionError:
            logger.warning(f"Redis no disponible (delete): clave '{self.get_cache_key()}'")

    def get_cache_key(self):
        return f"{self.cache_prefix}_{self.__class__.__name__}_list"

    # Métodos que los ViewSets pueden sobrescribir para personalizar comportamiento:

    def get_related_cache_keys(self, action, instance):
        """
        Override en ViewSets específicos para definir qué caches relacionados invalidar
        """
        return []

    def perform_additional_cache_invalidations(self, action, instance, instance_id=None):
        """
        Hook para invalidaciones personalizadas en ViewSets específicos
        """
        pass


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
        queryset = self.get_actives_queryset(request)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_actives_queryset(self, request)-> QuerySet:
        """
        Método Devuevlve un queryset con los objetos activos para que se le peuda agregar nuevos filtros
        """
        assert self.model is not None, (
            f"{self.__class__.__name__} debe definir un atributo 'model'."
        )
        manager = getattr(self.model, 'all_objects', self.model.objects)
        return manager.filter(is_removed=False)


# ¡ORDEN CORRECTO! Mixin primero, luego la clase base
class CachedViewSet(ListCacheMixin, AuthenticatedModelViewSet):
    """ViewSet base para catálogos con caché habilitado."""
    cache_timeout = 60 * 60 * 2  # 2 horas para catálogos