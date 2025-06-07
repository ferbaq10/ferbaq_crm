from rest_framework.viewsets import ModelViewSet
from catalog.models import (
    UDN, WorkCell, BusinessGroup, Division, Subdivision, Speciality,
    ProjectStatus, City, Period, StatusOpportunity
)
from catalog.serializers import (
    UDNSerializer, WorkCellSerializer, BusinessGroupSerializer, DivisionSerializer,
    SubdivisionSerializer, SpecialitySerializer, ProjectStatusSerializer, CitySerializer,
     PeriodSerializer, StatusOpportunitySerializer
)
from rest_framework.permissions import IsAuthenticated


class AuthenticatedModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

class UDNViewSet(AuthenticatedModelViewSet):
    queryset = UDN.objects.all()
    serializer_class = UDNSerializer

class WorkCellViewSet(AuthenticatedModelViewSet):
    queryset = WorkCell.objects.all()
    serializer_class = WorkCellSerializer

class BusinessGroupViewSet(AuthenticatedModelViewSet):
    queryset = BusinessGroup.objects.all()
    serializer_class = BusinessGroupSerializer

class DivisionViewSet(AuthenticatedModelViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer

class SubdivisionViewSet(AuthenticatedModelViewSet):
    queryset = Subdivision.objects.all()
    serializer_class = SubdivisionSerializer

class SpecialityViewSet(AuthenticatedModelViewSet):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer

class ProjectStatusViewSet(AuthenticatedModelViewSet):
    queryset = ProjectStatus.objects.all()
    serializer_class = ProjectStatusSerializer

class CityViewSet(AuthenticatedModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class PeriodViewSet(AuthenticatedModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer

class StatusOpportunityViewSet(AuthenticatedModelViewSet):
    queryset = StatusOpportunity.objects.all()
    serializer_class = StatusOpportunitySerializer
