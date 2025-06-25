from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from catalog.viewsets.base import AuthenticatedModelViewSet, CachedViewSet
from core.di import injector
from opportunity.services.opportunity_service import OpportunityService
from .models import Opportunity, CommercialActivity
from .serializers import (
    OpportunitySerializer,
    OpportunityWriteSerializer,
    CommercialActivitySerializer,
)


class OpportunityViewSet(CachedViewSet):
    model = Opportunity
    serializer_class = OpportunitySerializer

    GANADA_STATUS_ID = 5  # ID del estado 'Ganada'

    def get_serializer_class(self):
        return (
            OpportunitySerializer
            if self.action in ('list', 'retrieve')
            else OpportunityWriteSerializer
        )


    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            validated = serializer.validated_data

            validated['agent'] = request.user

            opportunity_service = injector.get(OpportunityService)
            opportunity = opportunity_service.process_update(instance, validated, request.data)
            return Response(self.get_serializer(opportunity).data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({'detail': 'Error de integridad en base de datos.'}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            print(e)
            return Response({'detail': 'Error interno del servidor.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommercialActivityViewSet(CachedViewSet):
    model = CommercialActivity
    serializer_class = CommercialActivitySerializer
