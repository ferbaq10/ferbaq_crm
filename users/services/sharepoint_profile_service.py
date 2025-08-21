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
    def _normalize_extension(extension: str) -> str:
        """Normaliza extensiones para consistencia"""
        extension = extension.lower().strip('.')
        # Convertir jpeg a jpg para consistencia
        if extension == 'jpeg':
            extension = 'jpg'
        return extension

    @staticmethod
    def upload_profile_photo(user_id: int, photo_file, file_extension: str) -> Optional[str]:
        """
        Sube foto de perfil a SharePoint en la ruta: users/profile_photos/
        Returns: URL completa del archivo en SharePoint o None si falla
        """
        try:
            # 1. Normalizar extensión para consistencia
            normalized_extension = SharePointProfileService._normalize_extension(file_extension)
            logger.info(f"📁 Subiendo foto para user_{user_id}: {file_extension} → {normalized_extension}")
            
            # 2. Autenticación
            logger.info(f"🔐 Iniciando autenticación con SharePoint...")
            ctx_auth = AuthenticationContext(SHAREPOINT_SITE_URL)
            if not ctx_auth.acquire_token_for_user(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD):
                raise Exception("Autenticación con SharePoint fallida")
            logger.info(f"✅ Autenticación exitosa")

            ctx = ClientContext(SHAREPOINT_SITE_URL, ctx_auth)

            # 3. Definir ruta específica para fotos de perfil
            folder_path = "users/profile_photos"
            folder_parts = folder_path.split("/")

            # 4. Ir al folder raíz
            site_path = urlparse(SHAREPOINT_SITE_URL).path.strip("/")
            root_relative_url = f"/{site_path}/{SHAREPOINT_DOC_LIB.strip()}"
            root_folder = ctx.web.get_folder_by_server_relative_url(root_relative_url)
            logger.info(f"📂 Accediendo a carpeta: {root_relative_url}")

            # 5. Crear carpetas
            logger.info(f"📁 Creando/accediendo carpetas: {folder_parts}")
            target_folder = ensure_folder(ctx, root_folder, folder_parts)

            # 6. Generar nombre único para la foto con extensión normalizada
            file_name = f"user_{user_id}_profile.{normalized_extension}"
            logger.info(f"📝 Nombre de archivo: {file_name}")

            # 7. Eliminar TODAS las posibles fotos anteriores (jpg, jpeg, png, webp)
            logger.info(f"🗑️ Eliminando fotos anteriores...")
            possible_extensions = ['jpg', 'jpeg', 'png', 'webp']
            for ext in possible_extensions:
                try:
                    old_file_name = f"user_{user_id}_profile.{ext}"
                    existing_file = target_folder.files.get_by_url(old_file_name)
                    existing_file.delete_object()
                    ctx.execute_query()
                    logger.info(f"🗑️ Foto anterior eliminada: {old_file_name}")
                except Exception as e:
                    # Es normal que no existan todas las extensiones
                    logger.info(f"ℹ️ No existía: {old_file_name} ({str(e)[:50]}...)")

            # 8. Subir nueva foto
            logger.info(f"⬆️ Iniciando subida del archivo...")
            try:
                file_stream = io.BytesIO(photo_file.read())
                logger.info(f"📊 Tamaño del archivo: {len(file_stream.getvalue())} bytes")
                
                uploaded_file = target_folder.upload_file(file_name, file_stream)
                logger.info(f"✅ Archivo uploaded_file creado, ejecutando query...")
                
                ctx.execute_query()
                logger.info(f"✅ Query ejecutado exitosamente")
                
                # 🔍 VERIFICAR que el archivo realmente existe después de subir
                try:
                    verification_file = target_folder.files.get_by_url(file_name)
                    ctx.execute_query()
                    logger.info(f"✅ VERIFICACIÓN: Archivo existe en SharePoint")
                except Exception as verify_error:
                    logger.error(f"❌ VERIFICACIÓN FALLÓ: El archivo NO existe después de subir: {verify_error}")
                    return None
                    
            except Exception as upload_error:
                logger.exception(f"❌ Error en el proceso de subida: {upload_error}")
                return None

            # 9. Construir URL completa con extensión normalizada
            full_url = f"{SHAREPOINT_SITE_URL}/{SHAREPOINT_DOC_LIB}/{folder_path}/{file_name}"

            logger.info(f"✅ Foto de perfil subida exitosamente: {full_url}")
            return full_url

        except Exception as e:
            logger.exception(f"❌ Error general subiendo foto de perfil: {e}")
            return None

    @staticmethod
    def delete_profile_photo(photo_url: str) -> bool:
        """Elimina foto de perfil de SharePoint usando tu función existente"""
        try:
            # Si la URL está vacía o es None, no hay nada que eliminar
            if not photo_url:
                return True
                
            from opportunity.sharepoint import _delete_file_from_sharepoint
            _delete_file_from_sharepoint(photo_url)
            logger.info(f"🗑️ Foto eliminada de SharePoint: {photo_url}")
            return True

        except Exception as e:
            # Log pero no fallar, ya que la foto podría no existir
            logger.warning(f"⚠️ No se pudo eliminar foto (posiblemente no existe): {e}")
            # Devolver True porque el objetivo (que no exista) se cumplió
            return True
        
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