from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework_simplejwt.views import TokenObtainPairView

from catalog.viewsets.base import CachedViewSet
from .serializers import MyTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from users.serializers import UserSerializer


User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



class UserViewSet(CachedViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], url_path='non-superusers', permission_classes=[IsAuthenticated, DjangoModelPermissions])
    def non_superusers(self, request):
        """
        Devuelve el listado de usuarios que no son superusuarios.
        Requiere permiso: auth.view_user
        """
        if not request.user.has_perm('auth.view_user'):
            raise PermissionDenied("No tiene permiso para ver usuarios.")
        users = User.objects.filter(is_superuser=False)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
