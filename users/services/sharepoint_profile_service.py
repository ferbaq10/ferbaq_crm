import logging
from typing import Optional
from urllib.parse import urlparse, unquote

from opportunity.sharepoint import SharePointManager

logger = logging.getLogger(__name__)


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
        Sube foto de perfil usando SharePointManager optimizado
        """
        try:
            # 1. Normalizar extensión
            normalized_extension = SharePointProfileService._normalize_extension(file_extension)

            # 2. Preparar datos
            file_content = photo_file.read()
            file_path = f"users/profile_photos/user_{user_id}_profile.{normalized_extension}"

            # 3. Eliminar fotos anteriores con otras extensiones
            possible_extensions = ['jpg', 'jpeg', 'png', 'webp']
            for ext in possible_extensions:
                if ext != normalized_extension:
                    old_path = f"users/profile_photos/user_{user_id}_profile.{ext}"
                    try:
                        result = SharePointManager.delete_file_by_path(old_path)
                        if result:
                            logger.info(f"Foto anterior eliminada: {old_path}")
                    except Exception as e:
                        logger.debug(f"No se pudo eliminar {old_path}: {e}")

            # 4. Subir nueva foto usando clase optimizada
            return SharePointManager.upload_file_to_sharepoint(
                file_path=file_path,
                file_data=file_content,
                replace_existing=True,
                verify_upload=True
            )

        except Exception as e:
            logger.exception(f"Error subiendo foto de perfil: {e}")
            return None

    @staticmethod
    def delete_profile_photo(photo_url: str) -> bool:
        """Elimina foto de perfil de SharePoint usando Microsoft Graph API"""
        try:
            # Si la URL está vacía o es None, no hay nada que eliminar
            if not photo_url:
                logger.info("URL vacía, no hay nada que eliminar")
                return True

            logger.info(f"Eliminando foto de SharePoint: {photo_url}")

            # 1. Procesar la URL para obtener la ruta del archivo
            parsed = urlparse(photo_url)
            full_path = unquote(parsed.path)

            # 2. Convertir ruta completa a ruta relativa a la biblioteca
            file_path = SharePointManager.site_relative_to_library_relative(
                full_path,
                "Biblioteca de Documentos"
            )

            logger.info(f"Ruta del archivo a eliminar: {file_path}")

            # 3. Usar metodo optimizado de la clase para eliminar
            success = SharePointManager.delete_file_by_path(file_path)

            if success:
                logger.info(f"Foto eliminada exitosamente: {photo_url}")
                return True
            else:
                logger.warning(f"No se pudo eliminar la foto: {photo_url}")
                # Devolver True porque el objetivo es que no exista
                return True
        except Exception as e:
            logger.warning(f"No se pudo eliminar foto (posiblemente no existe): {e}")
            # Devolver True porque el objetivo (que no exista) se cumplió
            return True

    @staticmethod
    def get_photo_content(photo_url: str) -> Optional[bytes]:
        """
        Obtiene contenido de foto usando SharePointManager optimizado
        """
        try:
            result = SharePointManager.get_file_content_from_sharepoint(
                file_url=photo_url,
                expected_content_type="image",
                timeout=30
            )

            if result:
                content, content_type = result
                logger.info(f"Foto obtenida: {len(content)} bytes, tipo: {content_type}")
                return content
            else:
                logger.warning(f"No se pudo obtener foto: {photo_url}")
                return None

        except Exception as e:
            logger.error(f"Error obteniendo foto: {e}")
            return None





