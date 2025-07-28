from django.contrib.auth import get_user_model
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from catalog.models import WorkCell
from catalog.viewsets.base import CachedViewSet
from core.di import injector
from users.serializers import UserSerializer, UserWithWorkcellSerializer
from users.services.user_service import UserService
from .permissions import CanAssignWorkcell, CanUnassignWorkcell
from .serializers import MyTokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserViewSet(CachedViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Configuración específica de User
    cache_prefix = "user"  # Override del "catalog" por defecto

    # Configuración para invalidaciones automáticas
    write_serializer_class = UserSerializer  # Para invalidaciones automáticas
    read_serializer_class = UserSerializer  # Para respuestas optimizadas

    @cached_property
    def user_service(self) -> UserService:
        return injector.get(UserService)

    @action(detail=False, methods=['get'], url_path='non-superusers')
    def non_superusers(self, request):
        """
        Devuelve el listado de usuarios que no son superusuarios.
        Requiere permiso: auth.view_user
        """
        try:
            users = self.user_service.get_non_superusers(request.user)
            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='users-with-workcell')
    def users_with_workcell(self, request):
        """
        Devuelve el listado de usuarios que tienen al menos una WorkCell asignada.
        Excluye superusuarios.
        Requiere permiso: auth.view_user
        """
        try:
            users = self.user_service.get_users_with_workcell()
            serializer = UserWithWorkcellSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True,
            methods=['post'],
            url_path='assign-workcell/(?P<workcell_id>[^/.]+)',
            permission_classes=[IsAuthenticated, CanAssignWorkcell])
    def assign_workcell(self, request, pk=None, workcell_id=None):
        """
        Asigna una WorkCell a un usuario (ManyToMany).

        URL: POST /api/users/{user_id}/assign-workcell/{workcell_id}/
        """
        try:
            user = self.get_object()
            try:
                workcell = self.user_service.assign_workcell(workcell_id, user)
            except WorkCell.DoesNotExist:
                return Response(
                    {"error": "La célula de trabajo no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": f"Célula '{workcell.name}' asignada al usuario {user.get_full_name()} correctamente."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'],
            url_path='unassign-workcell/(?P<workcell_id>[^/.]+)',
            permission_classes=[IsAuthenticated, CanUnassignWorkcell])
    def unassign_workcell(self, request, pk=None, workcell_id=None):
        """
        Desasigna una WorkCell de un usuario (ManyToMany).

        URL: DELETE /api/users/{user_id}/unassign-workcell/{workcell_id}/
        """
        try:
            user = self.get_object()
            workcell = self.user_service.unassign_workcell(workcell_id, user)

            return Response(
                {"message": f"Célula '{workcell.name}' desasignada del usuario {user.get_full_name()} correctamente."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
