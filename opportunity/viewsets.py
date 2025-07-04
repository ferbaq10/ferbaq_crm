from datetime import datetime

from django.db import transaction, IntegrityError
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from catalog.viewsets.base import CachedViewSet
from client.models import Client
from core.di import injector
from opportunity.services.opportunity_service import OpportunityService
from .models import Opportunity, CommercialActivity
from .serializers import (
    OpportunitySerializer, OpportunityWriteSerializer,
    CommercialActivitySerializer
)

class OpportunityViewSet(CachedViewSet):
    model = Opportunity
    serializer_class = OpportunitySerializer

    def get_base_optimized_queryset(self):
        optimized_clients = Prefetch(
            'contact__clients',
            queryset=Client.objects.select_related('city', 'business_group')
        )

        optimized_finance = Prefetch(
            'finance_data',
            queryset=self.model._meta.get_field('finance_data').related_model.objects.all()
        )

        return (Opportunity.objects.select_related(
            'status_opportunity',
            'currency',
            'opportunityType',
            'contact',
            'contact__job',
            'contact__city',
            'project',
            'project__client',
            'project__client__city',
            'project__client__business_group',
            'project__specialty',
            'project__subdivision',
            'project__subdivision__division',
            'project__project_status',
            'project__work_cell',
            'project__work_cell__udn'
        )
        .prefetch_related(
            optimized_finance,
            optimized_clients
        ))


    def get_optimized_queryset(self):
        return self.get_base_optimized_queryset().filter(
            created__year=datetime.now().year
        ).distinct().order_by('-created')


    def get_queryset(self):
        return self.get_optimized_queryset()


    def get_serializer_class(self):
        return (
            OpportunitySerializer
            if self.action in ('list', 'retrieve')
            else OpportunityWriteSerializer
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            file = request.FILES.get('document')

            opportunity_service = injector.get(OpportunityService)
            opportunity = opportunity_service.process_create(serializer, request, file)

            opportunity = self.get_base_optimized_queryset().get(pk=opportunity.pk)

            return Response(OpportunitySerializer(opportunity).data, status=status.HTTP_200_OK)

        except ValidationError as e:
            raise
        except IntegrityError:
            raise ValidationError({
                'non_field_errors': ['Error de integridad en base de datos.']
            })
        except Exception as e:
            print(f"[ERROR - create()]: {e}")
            raise APIException('Error interno del servidor.')


    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            partial = kwargs.pop('partial', request.method == 'PATCH')
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            file = request.FILES.get('document')

            opportunity_service = injector.get(OpportunityService)
            opportunity = opportunity_service.process_update(serializer, request.data, file)

            opportunity = self.get_base_optimized_queryset().get(pk=opportunity.pk)

            return Response(OpportunitySerializer(opportunity).data, status=status.HTTP_200_OK)

        except ValidationError as e:
            raise
        except IntegrityError:
            # Traducción la excepción de DB a un ValidationError de DRF
            raise ValidationError({
                'non_field_errors': ['Error de integridad en base de datos.']
            })
        except Exception as e:
            print(e)
            raise APIException('Error interno del servidor.')


class CommercialActivityViewSet(CachedViewSet):
    model = CommercialActivity
    serializer_class = CommercialActivitySerializer


