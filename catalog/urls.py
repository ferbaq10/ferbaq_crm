from rest_framework.routers import DefaultRouter
from catalog.viewsets import (
    UDNViewSet, WorkCellViewSet, BusinessGroupViewSet, DivisionViewSet,
    SubdivisionViewSet, SpecialityViewSet, ProjectStatusViewSet, CityViewSet,
    PeriodViewSet, StatusOpportunityViewSet
)

router = DefaultRouter()
router.register(r'udns', UDNViewSet)
router.register(r'workcells', WorkCellViewSet)
router.register(r'businessgroups', BusinessGroupViewSet)
router.register(r'divisions', DivisionViewSet)
router.register(r'subdivisions', SubdivisionViewSet)
router.register(r'specialities', SpecialityViewSet)
router.register(r'projectstatuses', ProjectStatusViewSet)
router.register(r'cities', CityViewSet)
router.register(r'periods', PeriodViewSet)
router.register(r'statusopportunities', StatusOpportunityViewSet)

urlpatterns = router.urls
