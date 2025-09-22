import logging
import os

from decouple import config
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from catalog.models import WorkCell
from catalog.viewsets.base import CachedViewSet
from core.di import injector
from opportunity.sharepoint import fetch_sharepoint_file
from users.serializers import (
    UserSerializer, UserWithWorkcellSerializer, UserProfileUpdateSerializer,
    ProfilePhotoUploadSerializer, PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer)
from users.services.user_service import UserService
from .permissions import CanAssignWorkcell, CanUnassignWorkcell
from .serializers import MyTokenObtainPairSerializer
from .services.sharepoint_profile_service import SharePointProfileService

logger = logging.getLogger(__name__)

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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Obtiene el perfil del usuario autenticado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Actualiza los datos del perfil del usuario autenticado"""
        serializer = UserProfileUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        # Devolver datos actualizados
        user_serializer = UserSerializer(request.user)
        return Response({
            'message': 'Perfil actualizado correctamente',
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_photo(self, request):
        """Sube foto de perfil a SharePoint"""
        serializer = ProfilePhotoUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        photo_file = serializer.validated_data['photo']
        file_extension = photo_file.name.split('.')[-1].lower()

        # Subir a SharePoint
        sharepoint_url = SharePointProfileService.upload_profile_photo(
            user_id=request.user.id,
            photo_file=photo_file,
            file_extension=file_extension
        )

        if not sharepoint_url:
            return Response(
                {'error': 'Error subiendo la foto a SharePoint'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Actualizar perfil del usuario
        profile = request.user.profile
        old_photo_url = profile.photo_sharepoint_url

        profile.photo_sharepoint_url = sharepoint_url
        profile.save()

       # Eliminar foto anterior si existía
       #  if old_photo_url:
       #      SharePointProfileService.delete_profile_photo(old_photo_url)

        # CORRECCIÓN: Devolver URL del proxy, no la directa de SharePoint
        filename = sharepoint_url.split('/')[-1]
        proxy_url = f"/api/users/photo/{filename}"

        return Response({
            'message': 'Foto subida correctamente',
            'photo_url': proxy_url  # ← Devolver URL del proxy
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def delete_photo(self, request):
        """Elimina foto de perfil del usuario autenticado"""
        profile = request.user.profile

        if not profile.photo_sharepoint_url:
            return Response(
                {'error': 'No hay foto para eliminar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Eliminar de SharePoint
        deleted = SharePointProfileService.delete_profile_photo(profile.photo_sharepoint_url)

        if deleted:
            profile.photo_sharepoint_url = None
            profile.save()
            return Response({'message': 'Foto eliminada correctamente'})
        else:
            return Response(
                {'error': 'Error eliminando la foto'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=False, methods=['get'], url_path='photo/(?P<filename>[^/]+)', 
        permission_classes=[AllowAny])  # ← Sin autenticación para fotos
    def get_photo(self, request, filename=None):
        """Proxy para servir fotos de perfil desde SharePoint - Endpoint público"""

        try:
            SHAREPOINT_SITE_URL = config("SHAREPOINT_SITE_URL")
            SHAREPOINT_DOC_LIB = config("SHAREPOINT_DOC_LIB", "Biblioteca de Documentos")
            
            # Construir URL completa del archivo
            photo_url = f"{SHAREPOINT_SITE_URL}/{SHAREPOINT_DOC_LIB}/users/profile_photos/{filename}"

            if photo_url:
                # Obtener el archivo de SharePoint
                photo_content = SharePointProfileService.get_photo_content(photo_url)

                content_type = 'image/jpeg'
                if photo_content:
                    if filename.lower().endswith('.png'):
                        content_type = 'image/png'
                    elif filename.lower().endswith('.webp'):
                        content_type = 'image/webp'
                    elif filename.lower().endswith('.gif'):
                        content_type = 'image/gif'

                response = HttpResponse(photo_content, content_type=content_type)
                response['Cache-Control'] = 'max-age=3600'  # Cache por 1 hora
                response['Access-Control-Allow-Origin'] = '*'  # Para CORS
                return response
            else:
                return self.serve_default_avatar()
                
        except Exception as e:
            logger.exception(f"Error en proxy de foto: {e}")
            #return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return self.serve_default_avatar()

    def serve_default_avatar(self):
        """Sirve una imagen avatar por defecto"""
        default_photo_path = os.path.join(settings.STATIC_ROOT, 'images', 'default-avatar.jpg')

        if os.path.exists(default_photo_path):
            with open(default_photo_path, 'rb') as f:
                return HttpResponse(f.read(), content_type='image/jpeg')
        else:
            # SVG avatar por defecto
            default_svg = '''
            <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="40" fill="#ccc"/>
                <circle cx="50" cy="40" r="15" fill="#999"/>
                <path d="M25 75 Q50 60 75 75" stroke="#999" stroke-width="8" fill="none"/>
            </svg>
            '''
            return HttpResponse(default_svg, content_type='image/svg+xml')
        
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Cambia la contraseña del usuario autenticado"""
        serializer = PasswordChangeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Actualizar contraseña
            serializer.save(user=request.user)
            
            return Response({
                'message': 'Contraseña actualizada correctamente'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Error cambiando contraseña para usuario {request.user.username}: {e}")
            
            return Response({
                'error': 'Error interno del servidor al cambiar la contraseña'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def password_reset_request(self, request):
        """Solicitar restablecimiento de contraseña por email"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            serializer.save()
            return Response({
                'message': 'Si el correo existe en nuestro sistema, recibirás un enlace para restablecer tu contraseña.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Error en password reset request: {e}")
            
            return Response({
                'error': 'Error interno del servidor al procesar la solicitud.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def password_reset_confirm(self, request):
        """Confirmar restablecimiento de contraseña con token"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            serializer.save()
            return Response({
                'message': 'Contraseña restablecida correctamente. Ya puedes iniciar sesión.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Error en password reset confirm: {e}")
            
            return Response({
                'error': 'Error interno del servidor al restablecer la contraseña.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=['get'], url_path='sharepoint-image')
    def proxy_sharepoint_image(self, request):
        url = request.GET.get("url")
        if not url:
            return HttpResponse("URL is required", status=400)

        try:
            blob, content_type = fetch_sharepoint_file(url)

            # Validar que sea imagen
            if not content_type.startswith("image/"):
                # Puedes intentar deducir por extensión si lo prefieres
                logger.warning(f"No es imagen. Content-Type: {content_type}")
                return HttpResponse("La URL no tiene una imagen", status=404)

            resp = HttpResponse(blob, content_type=content_type)
            resp["Cache-Control"] = "public, max-age=900"
            resp["Access-Control-Allow-Origin"] = "*"
            return resp

        except Exception as e:
            logger.error(f"Error al obtener la imagen: {e}")
            # Si es auth, devuelve 401 para diferenciarlos
            msg = str(e)
            if "Autenticación" in msg or "Unauthorized" in msg:
                return HttpResponse("Requiere autenticación con SharePoint", status=401)
            return HttpResponse("Error al obtener la imagen", status=500)