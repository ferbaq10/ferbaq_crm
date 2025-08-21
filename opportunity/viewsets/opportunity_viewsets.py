import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException, PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response

from catalog.viewsets.base import CachedViewSet
from core.di import injector
from opportunity.models import Opportunity, CommercialActivity
from opportunity.permissions import CanAccessOpportunity
from opportunity.serializers import (
    OpportunitySerializer, OpportunityWriteSerializer,
    CommercialActivitySerializer
)
from opportunity.services.opportunity_service import OpportunityService
from users.models import RoleScope
from users.services.access import resolve_scope

logger = logging.getLogger(__name__)

class OpportunityViewSet(CachedViewSet):
    model = Opportunity
    serializer_class = OpportunitySerializer

    permission_classes = [IsAuthenticated, DjangoModelPermissions, CanAccessOpportunity]

    # Configuración específica de Opportunity
    cache_prefix = "opportunity"  # Override del "catalog" por defecto

    # Configuración para invalidaciones automáticas
    write_serializer_class = OpportunityWriteSerializer  # Para invalidaciones automáticas
    read_serializer_class = OpportunitySerializer  # Para respuestas optimizadas

    @cached_property
    def opportunity_service(self) -> OpportunityService:
        return injector.get(OpportunityService)

    # --- OBJETO (detalle) SIN FILTRO DE ROL + chequeo de permiso de objeto ---
    def get_object(self):
        lookup = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        try:
            obj = self.opportunity_service.get_prefetched_queryset().get(**{self.lookup_field: lookup})
        except ObjectDoesNotExist:
            raise NotFound('Opportunity no encontrada.')

        # chequeo de alcance (igual que en CanAccessOpportunity, por si cambias permisos)
        user = self.request.user
        scope = resolve_scope(user)
        if user.is_superuser or scope == RoleScope.ALL:
            return obj
        if scope == RoleScope.OWNED and obj.agent_id == user.id:
            return obj
        if scope == RoleScope.WORKCELL:
            wc = getattr(getattr(obj, 'project', None), 'work_cell', None)
            if wc and wc.users.filter(id=user.id).exists():
                return obj
        raise PermissionDenied('No tienes permisos para esta oportunidad.')

        # checar permiso equivalente a tu add_filter_by_rol
        scope = resolve_scope(self.request.user)
        if self.request.user.is_superuser or scope == RoleScope.ALL:
            return obj
        if scope == RoleScope.OWNED and obj.agent_id == self.request.user.id:
            return obj
        if scope == RoleScope.WORKCELL:
            wc = getattr(getattr(obj, 'project', None), 'work_cell', None)
            if wc and wc.users.filter(id=self.request.user.id).exists():
                return obj
        raise PermissionDenied('No tienes permisos para esta oportunidad.')


    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'action', None) == 'list':
            return self.opportunity_service.get_filtered_queryset(user)
        return self.opportunity_service.get_prefetched_queryset()


    def get_serializer_class(self):
        return (
            self.read_serializer_class
            if self.action in ('list', 'retrieve')
            else self.write_serializer_class
        )

    def get_actives_queryset(self, request):
        # si esta función solo se usa para listados “activos”
        user = request.user
        return self.opportunity_service.get_filtered_queryset(user).filter(is_removed=False).distinct()


    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = self.get_serializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            files_documents = request.FILES.getlist('documents')

            opportunity = self.opportunity_service.process_create(serializer, request, files_documents)

            # recarga con prefetch (sin rol) para devolver respuesta completa y consistente
            opportunity = self.opportunity_service.get_prefetched_queryset().get(pk=opportunity.pk)

            return Response(OpportunitySerializer(opportunity).data, status=status.HTTP_200_OK)

        except ValidationError as e:
            logger.exception("[ValidationError - create()] {e}")
            raise
        except IntegrityError as e:
            logger.exception(f"[IntegrityError - create()] {e}")
            raise ValidationError({
                'non_field_errors': ['Error de IntegrityError ValidationError en base de datos.']
            })
        except Exception as e:
            logger.exception(f"[ERROR - create()]{e}")
            raise APIException('Error - create() interno del servidor.')


    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            user = self.request.user
            # get_object() personalizado NO filtra por rol y valida permisos
            instance = self.get_object()
            partial = kwargs.pop('partial', request.method == 'PATCH')
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            files = request.FILES.getlist('documents')

            opportunity = self.opportunity_service.process_update(serializer, request.data, files)

            # recarga con prefetch (sin rol) para respuesta consistente
            opportunity = self.opportunity_service.get_prefetched_queryset().get(pk=opportunity.pk)

            return Response(OpportunitySerializer(opportunity).data, status=status.HTTP_200_OK)

        except ValidationError as e:
            raise
        except IntegrityError as e:
            logger.exception(f"[IntegrityError - update()] {e}")
            raise ValidationError({
                'non_field_errors': ['Error de integridad en base de datos.']
            })
        except PermissionDenied as e:
            logger.exception(f"[PermissionDenied - update()] {e}")
            raise
        except Exception as e:
            logger.exception(f"[ERROR - update()]{e}")
            raise APIException('Error interno del servidor.')

class CommercialActivityViewSet(CachedViewSet):
    model = CommercialActivity
    serializer_class = CommercialActivitySerializer


