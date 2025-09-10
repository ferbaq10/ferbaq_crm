from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from catalog.models import (
    UDN, WorkCell, BusinessGroup, Division, Subdivision, Specialty,
    ProjectStatus, City, Period, StatusOpportunity, Currency, Job, OpportunityType,
    MeetingType, MeetingResult, LostOpportunityType, PurchaseStatusType
)
from catalog.serializers import (
    UDNSerializer, WorkCellSerializer, BusinessGroupSerializer, DivisionSerializer,
    SubdivisionSerializer, SpecialtySerializer, ProjectStatusSerializer, CitySerializer,
    PeriodSerializer, StatusOpportunitySerializer, CurrencySerializer, JobSerializer, OpportunityTypeSerializer,
    MeetingTypeSerializer, MeetingResultSerializer, LostOpportunityTypeSerializer, PurchaseStatusTypeSerializer,
    WorkCellWriteSerializer
)
from catalog.viewsets.base import CachedViewSet


class UDNViewSet(CachedViewSet):
    model = UDN
    serializer_class = UDNSerializer


class WorkCellViewSet(CachedViewSet):
    model = WorkCell
    serializer_class = WorkCellSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return WorkCellSerializer
        return WorkCellWriteSerializer


    def get_actives_queryset(self, request):
        return WorkCell.all_objects.filter(users=request.user).filter(is_removed=False).distinct()

    @action(detail=False, methods=['get'], url_path='workcell-active-all')
    def workcell_active_all(self, request):
        """
            Devolver la lista de workcell activas del sistema.
        """
        try:
            result = WorkCell.all_objects.filter(is_removed=False).distinct()
            serializer = WorkCellSerializer(result, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BusinessGroupViewSet(CachedViewSet):
    model = BusinessGroup
    serializer_class = BusinessGroupSerializer

class DivisionViewSet(CachedViewSet):
    model = Division
    serializer_class = DivisionSerializer

class SubdivisionViewSet(CachedViewSet):
    model = Subdivision
    serializer_class = SubdivisionSerializer

class SpecialtyViewSet(CachedViewSet):
    model = Specialty
    serializer_class = SpecialtySerializer

class ProjectStatusViewSet(CachedViewSet):
    model = ProjectStatus
    serializer_class = ProjectStatusSerializer

class CityViewSet(CachedViewSet):
    model = City
    serializer_class = CitySerializer

class PeriodViewSet(CachedViewSet):
    model = Period
    serializer_class = PeriodSerializer

class StatusOpportunityViewSet(CachedViewSet):
    model = StatusOpportunity
    serializer_class = StatusOpportunitySerializer

class CurrencyViewSet(CachedViewSet):
    model = Currency
    serializer_class = CurrencySerializer


class JobViewSet(CachedViewSet):
    model = Job
    serializer_class = JobSerializer


class OpportunityTypeViewSet(CachedViewSet):
    model = OpportunityType
    serializer_class = OpportunityTypeSerializer


class MeetingTypeViewSet(CachedViewSet):
    model = MeetingType
    serializer_class = MeetingTypeSerializer


class MeetingResultViewSet(CachedViewSet):
    model = MeetingResult
    serializer_class = MeetingResultSerializer


class LostOpportunityTypeViewSet(CachedViewSet):
    model = LostOpportunityType
    serializer_class = LostOpportunityTypeSerializer


class PurchaseStatusTypeViewSet(CachedViewSet):
    model = PurchaseStatusType
    serializer_class = PurchaseStatusTypeSerializer
