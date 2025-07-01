from catalog.models import (
    UDN, WorkCell, BusinessGroup, Division, Subdivision, Specialty,
    ProjectStatus, City, Period, StatusOpportunity, Currency, Job, OpportunityType,
    MeetingType, MeetingResult, LostOpportunityType, PurchaseStatusType
)
from catalog.serializers import (
    UDNSerializer, WorkCellSerializer, BusinessGroupSerializer, DivisionSerializer,
    SubdivisionSerializer, SpecialtySerializer, ProjectStatusSerializer, CitySerializer,
    PeriodSerializer, StatusOpportunitySerializer, CurrencySerializer, JobSerializer, OpportunityTypeSerializer,
    MeetingTypeSerializer, MeetingResultSerializer, LostOpportunityTypeSerializer, PurchaseStatusTypeSerializer
)
from catalog.viewsets.base import CachedViewSet, AuthenticatedModelViewSet


class UDNViewSet(CachedViewSet):
    model = UDN
    serializer_class = UDNSerializer

class WorkCellViewSet(CachedViewSet):
    model = WorkCell
    serializer_class = WorkCellSerializer

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
