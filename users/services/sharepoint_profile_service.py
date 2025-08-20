import io
import logging
from typing import Optional
from decouple import config
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from urllib.parse import urlparse
from opportunity.sharepoint import ensure_folder  # Reutilizar tu función existente

logger = logging.getLogger(__name__)

SHAREPOINT_SITE_URL = config("SHAREPOINT_SITE_URL")
SHAREPOINT_DOC_LIB = config("SHAREPOINT_DOC_LIB", "Biblioteca de Documentos")
SHAREPOINT_USERNAME = config("SHAREPOINT_USERNAME")
SHAREPOINT_PASSWORD = config("SHAREPOINT_PASSWORD")


class SharePointProfileService:

    @staticmethod
    def upload_profile_photo(user_id: int, photo_file, file_extension: str) -> Optional[str]:
        """
        Sube foto de perfil a SharePoint en la ruta: users/profile_photos/
        Returns: URL completa del archivo en SharePoint o None si falla
        """
        try:
            # 1. Autenticación (igual que tu código existente)
            ctx_auth = AuthenticationContext(SHAREPOINT_SITE_URL)
            if not ctx_auth.acquire_token_for_user(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD):
                raise Exception("Autenticación con SharePoint fallida")

            ctx = ClientContext(SHAREPOINT_SITE_URL, ctx_auth)

            # 2. Definir ruta específica para fotos de perfil
            folder_path = "users/profile_photos"
            folder_parts = folder_path.split("/")

            # 3. Ir al folder raíz (igual que tu implementación)
            site_path = urlparse(SHAREPOINT_SITE_URL).path.strip("/")
            root_relative_url = f"/{site_path}/{SHAREPOINT_DOC_LIB.strip()}"
            root_folder = ctx.web.get_folder_by_server_relative_url(root_relative_url)

            # 4. Crear carpetas usando tu función existente
            target_folder = ensure_folder(ctx, root_folder, folder_parts)

            # 5. Generar nombre único para la foto
            file_name = f"user_{user_id}_profile.{file_extension}"

            # 6. Eliminar foto anterior si existe
            try:
                existing_file = target_folder.files.get_by_url(file_name)
                existing_file.delete_object()
                ctx.execute_query()
                logger.info(f"🗑️ Foto anterior eliminada: {file_name}")
            except Exception:
                logger.info(f"ℹ️ No había foto anterior para user_{user_id}")

            # 7. Subir nueva foto
            file_stream = io.BytesIO(photo_file.read())
            uploaded_file = target_folder.upload_file(file_name, file_stream)
            ctx.execute_query()

            # 8. Construir URL completa
            full_url = f"{SHAREPOINT_SITE_URL}/{SHAREPOINT_DOC_LIB}/{folder_path}/{file_name}"

            logger.info(f"✅ Foto de perfil subida: {full_url}")
            return full_url

        except Exception as e:
            logger.exception(f"❌ Error subiendo foto de perfil: {e}")
            return None

    @staticmethod
    def delete_profile_photo(photo_url: str) -> bool:
        """Elimina foto de perfil de SharePoint usando tu función existente"""
        try:
            from opportunity.sharepoint import _delete_file_from_sharepoint
            _delete_file_from_sharepoint(photo_url)
            logger.info(f"🗑️ Foto eliminada de SharePoint: {photo_url}")
            return True

        except Exception as e:
            logger.exception(f"❌ Error eliminando foto: {e}")
            return False
        
    @staticmethod
    def get_photo_content(photo_url: str) -> Optional[bytes]:
        """Obtiene el contenido binario de una foto desde SharePoint"""
        try:
            from urllib.parse import urlparse, unquote
            
            parsed = urlparse(photo_url)
            relative_url = unquote(parsed.path)

            ctx_auth = AuthenticationContext(SHAREPOINT_SITE_URL)
            if not ctx_auth.acquire_token_for_user(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD):
                logger.error("❌ Falló autenticación con SharePoint")
                return None

            ctx = ClientContext(SHAREPOINT_SITE_URL, ctx_auth)
            file = ctx.web.get_file_by_server_relative_url(relative_url)
            
            # Obtener contenido del archivo
            content = file.get_content()
            ctx.execute_query()
            
            logger.info(f"✅ Foto obtenida exitosamente: {len(content.value)} bytes")
            return content.value
            
        except Exception as e:
            logger.exception(f"❌ Error obteniendo foto: {e}")
            return None