from django.db.models import Q
from rest_framework import serializers
from django.core.cache import cache
from django.conf import settings
import logging

from catalog.serializers import CitySerializer, BusinessGroupSerializer
from project.serializers import ProjectSerializer
from .models import Client, City, BusinessGroup
from core.serializers.cache_mixin import CacheInvalidationMixin


logger = logging.getLogger(__name__)


class ClientSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    business_group = BusinessGroupSerializer()
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = [
            'id',
            'rfc',
            'city',
            'company',
            'projects',
            'id_client',
            'is_removed',
            'business_group'
        ]
        read_only_fields = ['created', 'modified']


class ClientWriteSerializer(CacheInvalidationMixin, serializers.ModelSerializer):
    """
    Serializer híbrido que detecta automáticamente si Redis está disponible
    y optimiza en consecuencia - MÁXIMO 2 consultas siempre
    """
    cache_keys = [
        "cities_ids_cache_v1",
        "business_groups_ids_cache_v1"
    ]

    projects = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar querysets con detección automática de Redis
        self.fields['city'].queryset = self.get_cities_queryset()
        self.fields['business_group'].queryset = self.get_business_groups_queryset()

    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.none(),  # Se configura en __init__
        write_only=True,
        required=False,
        allow_null=True
    )
    business_group = serializers.PrimaryKeyRelatedField(
        queryset=BusinessGroup.objects.none(),  # Se configura en __init__
        write_only=True
    )

    class Meta:
        model = Client
        fields = [
            'id',
            'rfc',
            'city',
            'company',
            'projects',
            'id_client',
            'is_removed',
            'business_group'
        ]
        read_only_fields = ['created']



    @classmethod
    def is_redis_available(cls):
        """
        Detecta si Redis está disponible y funcionando
        """
        try:
            # Verificar si hay configuración de Redis
            cache_backend = getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', '')
            if 'redis' not in cache_backend.lower():
                return False

            # Test rápido de conectividad
            cache.set('redis_test_key', 'test', 1)
            result = cache.get('redis_test_key')
            cache.delete('redis_test_key')
            return result == 'test'

        except Exception as e:
            logger.debug(f"Redis no disponible: {e}")
            return False

    def get_cities_queryset(self):
        """
        Obtiene queryset de ciudades con cache inteligente
        """
        if not self.is_redis_available():
            # Sin Redis: queryset directo (muy eficiente)
            return City.objects.all()

        # Con Redis: usar cache optimizado
        cache_key = "cities_ids_cache_v1"

        try:
            cached_ids = cache.get(cache_key)
            if cached_ids is not None:
                logger.debug(f"[Cache HIT] Ciudades: {len(cached_ids)} IDs")
                return City.objects.filter(id__in=cached_ids)

            # Cache miss: almacenar solo IDs
            city_ids = list(City.objects.values_list('id', flat=True))
            cache.set(cache_key, city_ids, 60 * 30)  # 30 minutos
            logger.info(f"[Cache SET] Ciudades: {len(city_ids)} IDs cacheados")

            return City.objects.filter(id__in=city_ids)

        except Exception as e:
            logger.warning(f"Error en cache de ciudades: {e}")
            return City.objects.all()

    def get_business_groups_queryset(self):
        """
        Obtiene queryset de grupos empresariales con cache inteligente
        """
        if not self.is_redis_available():
            # Sin Redis: queryset directo (muy eficiente)
            return BusinessGroup.objects.all()

        # Con Redis: usar cache optimizado
        cache_key = "business_groups_ids_cache_v1"

        try:
            cached_ids = cache.get(cache_key)
            if cached_ids is not None:
                logger.debug(f"[Cache HIT] Grupos: {len(cached_ids)} IDs")
                return BusinessGroup.objects.filter(id__in=cached_ids)

            # Cache miss: almacenar solo IDs
            group_ids = list(BusinessGroup.objects.values_list('id', flat=True))
            cache.set(cache_key, group_ids, 60 * 30)  # 30 minutos
            logger.info(f"[Cache SET] Grupos: {len(group_ids)} IDs cacheados")

            return BusinessGroup.objects.filter(id__in=group_ids)

        except Exception as e:
            logger.warning(f"Error en cache de grupos: {e}")
            return BusinessGroup.objects.all()

    def validate(self, attrs):
        """
        Validación ultra-optimizada: MÁXIMO 2 consultas
        """
        rfc = attrs.get('rfc')
        company = attrs.get('company')
        id_client = attrs.get('id_client')

        # Early return si no hay campos únicos que validar
        if not any([rfc, company, id_client]):
            return attrs

        # Construir query optimizada
        base_queryset = Client.objects.all()
        if self.instance:
            base_queryset = base_queryset.exclude(pk=self.instance.pk)

        # Construir filtros solo para campos presentes
        conflicts_query = Q()
        if rfc:
            conflicts_query |= Q(rfc=rfc)
        if company:
            conflicts_query |= Q(company=company)
        if id_client:
            conflicts_query |= Q(id_client=id_client)

        # CONSULTA 1: Verificar si existen conflictos (muy rápida)
        if not base_queryset.filter(conflicts_query).exists():
            return attrs

        # CONSULTA 2: Solo si hay conflictos, obtener los valores para errores específicos
        conflicting_clients = base_queryset.filter(conflicts_query).values('rfc', 'company', 'id_client')

        errors = {}
        for client in conflicting_clients:
            if rfc and client['rfc'] == rfc:
                errors['rfc'] = 'Ya existe un cliente con este RFC'
            if company and client['company'] == company:
                errors['company'] = 'Ya existe un cliente con esta razón social'
            if id_client and client['id_client'] == id_client:
                errors['id_client'] = 'Ya existe un cliente con este ID'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
