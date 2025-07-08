from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from catalog.models import WorkCell
from catalog.viewsets.base import CachedViewSet
from users.serializers import UserSerializer
from .serializers import MyTokenObtainPairSerializer

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

    @action(detail=True, methods=['post'], url_path='assign-workcell/(?P<workcell_id>[^/.]+)')
    def assign_workcell(self, request, pk=None, workcell_id=None):
        """
        Asigna una WorkCell a un usuario (ManyToMany).

        URL: POST /api/users/{user_id}/assign-workcell/{workcell_id}/
        """
        try:
            user = self.get_object()
            try:
                workcell = WorkCell.objects.get(pk=workcell_id)
            except WorkCell.DoesNotExist:
                return Response(
                    {"error": "La célula de trabajo no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Asignar sin sobrescribir otras células si deseas agregar (usa .add())
            user.workcell.add(workcell)

            return Response(
                {"message": f"Célula '{workcell.name}' asignada al usuario {user.get_full_name()} correctamente."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
