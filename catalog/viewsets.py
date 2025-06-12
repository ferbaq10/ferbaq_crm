from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from catalog.models import (
    UDN, WorkCell, BusinessGroup, Division, Subdivision, Specialty,
    ProjectStatus, City, Period, StatusOpportunity, Currency
)
from catalog.serializers import (
    UDNSerializer, WorkCellSerializer, BusinessGroupSerializer, DivisionSerializer,
    SubdivisionSerializer, SpecialtySerializer, ProjectStatusSerializer, CitySerializer,
    PeriodSerializer, StatusOpportunitySerializer, CurrencySerializer
)


class AuthenticatedModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = None  # Este se define en la subclase

    def get_queryset(self):
        assert self.model is not None, (
            f"{self.__class__.__name__} debe definir un atributo 'model'."
        )
        # Verifica si el modelo tiene el manager `all_objects`, si no usa `objects`
        manager = getattr(self.model, 'all_objects', self.model.objects)
        return manager.all()

    @action(detail=False, methods=['get'], url_path='actives')
    def actives(self, request):
        assert self.model is not None, (
            f"{self.__class__.__name__} debe definir un atributo 'model'."
        )
        manager = getattr(self.model, 'all_objects', self.model.objects)
        queryset = manager.filter(is_removed=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UDNViewSet(AuthenticatedModelViewSet):
    model = UDN
    serializer_class = UDNSerializer

class WorkCellViewSet(AuthenticatedModelViewSet):
    model = WorkCell
    serializer_class = WorkCellSerializer

class BusinessGroupViewSet(AuthenticatedModelViewSet):
    model = BusinessGroup
    serializer_class = BusinessGroupSerializer

class DivisionViewSet(AuthenticatedModelViewSet):
    model = Division
    serializer_class = DivisionSerializer

class SubdivisionViewSet(AuthenticatedModelViewSet):
    model = Subdivision
    serializer_class = SubdivisionSerializer

class SpecialtyViewSet(AuthenticatedModelViewSet):
    model = Specialty
    serializer_class = SpecialtySerializer

class ProjectStatusViewSet(AuthenticatedModelViewSet):
    model = ProjectStatus
    serializer_class = ProjectStatusSerializer

class CityViewSet(AuthenticatedModelViewSet):
    model = City
    serializer_class = CitySerializer


class PeriodViewSet(AuthenticatedModelViewSet):
    model = Period
    serializer_class = PeriodSerializer

class StatusOpportunityViewSet(AuthenticatedModelViewSet):
    model = StatusOpportunity
    serializer_class = StatusOpportunitySerializer


class StatusOpportunityViewSet(AuthenticatedModelViewSet):
    model = StatusOpportunity
    serializer_class = StatusOpportunitySerializer


class CurrencyViewSet(AuthenticatedModelViewSet):
    model = Currency
    serializer_class = CurrencySerializer
