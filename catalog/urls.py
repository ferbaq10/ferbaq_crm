from rest_framework.routers import DefaultRouter
from catalog.viewsets import (
    UDNViewSet, WorkCellViewSet, BusinessGroupViewSet, DivisionViewSet,
    SubdivisionViewSet, SpecialityViewSet, ProjectStatusViewSet, CityViewSet,
    PeriodViewSet, StatusOpportunityViewSet
)

router = DefaultRouter()
router.register(r'udns', UDNViewSet, basename='udn')
router.register(r'workcells', WorkCellViewSet, basename='workcell')
router.register(r'business-groups', BusinessGroupViewSet, basename='businessgroup')
router.register(r'divisions', DivisionViewSet, basename='division')
router.register(r'subdivisions', SubdivisionViewSet, basename='subdivision')
router.register(r'specialities', SpecialityViewSet, basename='speciality')
router.register(r'project-statuses', ProjectStatusViewSet, basename='projectstatus')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'periods', PeriodViewSet, basename='period')
router.register(r'status-opportunities', StatusOpportunityViewSet, basename='statusopportunity')


urlpatterns = router.urls
