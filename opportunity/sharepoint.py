import logging
from decouple import config

SHAREPOINT_SITE_URL = config("SHAREPOINT_SITE_URL")
CLIENT_ID = config("SHAREPOINT_CLIENT_ID")
CLIENT_SEC = config("SHAREPOINT_CLIENT_SECRET")
TENANT_ID = config("SHAREPOINT_TENANT_ID")  # o usar el dominio
HOSTNAME = config("HOSTNAME")  # tu tenant host
SITE_PATH = config("SITE_PATH")
SHAREPOINT_DOC_LIB = config("SHAREPOINT_DOC_LIB", "Biblioteca de Documentos")


DOC_LIB_DISPLAY_NAME = None  # Ej: "Documentos" o "Shared Documents" si quieres forzar

logger = logging.getLogger(__name__)

import logging
import threading
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
import time

from decouple import config
from urllib.parse import urlparse, unquote, quote
import requests
import msal

# Configuración global
SHAREPOINT_SITE_URL = config("SHAREPOINT_SITE_URL")
CLIENT_ID = config("SHAREPOINT_CLIENT_ID")
CLIENT_SEC = config("SHAREPOINT_CLIENT_SECRET")
TENANT_ID = config("SHAREPOINT_TENANT_ID")
HOSTNAME = config("HOSTNAME")
SITE_PATH = config("SITE_PATH")
SHAREPOINT_DOC_LIB = config("SHAREPOINT_DOC_LIB", "Biblioteca de Documentos")

DOC_LIB_DISPLAY_NAME = None

logger = logging.getLogger(__name__)


@dataclass
class SharePointConfig:
    """Configuración centralizada para SharePoint"""
    token: str
    site_id: str
    drive_id: str
    expires_at: float


class SharePointManager:
    """
    Gestor centralizado para operaciones de SharePoint usando Microsoft Graph API
    """
    _lock = threading.Lock()
    _config: Optional[SharePointConfig] = None
    _token_refresh_buffer = 300  # Renovar 5 minutos antes del vencimiento

    @classmethod
    def get_fresh_token(cls) -> Tuple[str, float]:
        """
        Obtiene un nuevo token de Graph API

        Returns:
            Tupla (token, expires_at)
        """
        app = msal.ConfidentialClientApplication(
            client_id=CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{TENANT_ID}",
            client_credential=CLIENT_SEC,
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

        if "access_token" not in result:
            raise RuntimeError(f"No se pudo obtener token Graph: {result}")

        # Los tokens de aplicación de Azure duran 3600 segundos (1 hora)
        expires_at = time.time() + result.get("expires_in", 3600) - cls._token_refresh_buffer
        return result["access_token"], expires_at

    @classmethod
    def is_config_valid(cls) -> bool:
        """Verifica si la configuración actual es válida"""
        if not cls._config:
            return False
        return time.time() < cls._config.expires_at

    @classmethod
    def get_site_id(cls, token: str) -> str:
        """
        Obtiene el ID del sitio de SharePoint

        Args:
            token: Token de autenticación

        Returns:
            ID del sitio
        """
        url = f"https://graph.microsoft.com/v1.0/sites/{HOSTNAME}:/sites/{SITE_PATH}"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        response.raise_for_status()
        return response.json()["id"]

    @classmethod
    def get_drive_id(cls, token: str, site_id: str, preferred_name: str = None) -> str:
        """
        Obtiene el ID del drive de la biblioteca de documentos

        Args:
            token: Token de autenticación
            site_id: ID del sitio
            preferred_name: Nombre preferido de la biblioteca

        Returns:
            ID del drive
        """
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        response.raise_for_status()
        drives = response.json().get("value", [])

        # Buscar por nombre preferido
        if preferred_name:
            for drive in drives:
                if drive.get("name", "").lower() == preferred_name.lower():
                    return drive["id"]

        # Buscar drive de biblioteca por defecto
        for drive in drives:
            if drive.get("driveType") == "documentLibrary" and drive.get("name"):
                return drive["id"]

        raise RuntimeError(f"No se encontró drive. Drives disponibles: {[d.get('name') for d in drives]}")

    @classmethod
    def get_config(cls, force_refresh: bool = False) -> SharePointConfig:
        """
        Obtiene configuración completa (token, site_id, drive_id) con cache automático

        Args:
            force_refresh: Si True, fuerza renovación de la configuración

        Returns:
            Configuración de SharePoint
        """
        with cls._lock:
            # Si tenemos configuración válida y no se fuerza refresh, devolverla
            # if not force_refresh and cls.is_config_valid():
            #     return cls._config

            try:
                logger.info("Renovando configuración de SharePoint...")

                # Obtener nuevo token
                token, expires_at = cls.get_fresh_token()

                # Obtener site_id y drive_id
                site_id = cls.get_site_id(token)
                drive_id = cls.get_drive_id(token, site_id, "Biblioteca de Documentos")

                # Crear nueva configuración
                cls._config = SharePointConfig(
                    token=token,
                    site_id=site_id,
                    drive_id=drive_id,
                    expires_at=expires_at
                )

                logger.info(f"Configuración renovada. Expira en: {(expires_at - time.time()) / 60:.1f} minutos")
                return cls._config

            except Exception as e:
                logger.error(f"Error renovando configuración SharePoint: {e}")
                raise

    @classmethod
    def get_auth_headers(cls) -> dict:
        """
        Obtiene headers de autenticación

        Returns:
            Diccionario con headers de autorización
        """
        if cls._config is None or cls._config.token is None:
            SharePointManager.get_config()
        return {"Authorization": f"Bearer {cls._config.token}"}

    @classmethod
    def build_graph_url(cls, path: str, endpoint: str = "") -> str:
        """
        Construye URL de Graph API para el archivo/carpeta especificado

        Args:
            path: Ruta del archivo/carpeta
            endpoint: Endpoint adicional (ej: "/content")

        Returns:
            URL completa de Graph API
        """
        config = cls.get_config()
        base_url = f"https://graph.microsoft.com/v1.0/sites/{config.site_id}/drives/{config.drive_id}/root"

        if path:
            encoded_path = quote(path, safe="/()!$'*,;=:@&+")
            return f"{base_url}:/{encoded_path}:{endpoint}"
        else:
            return f"{base_url}{endpoint}"

    @classmethod
    def site_relative_to_library_relative(cls, full_path: str, library_display_hint: str = None) -> str:
        """
        Convierte path completo del sitio a path relativo de la biblioteca

        Args:
            full_path: Path completo (ej: /sites/FERBAQ/Biblioteca de Documentos/archivo.pdf)
            library_display_hint: Nombre de la biblioteca para ayudar en la conversión

        Returns:
            Path relativo a la biblioteca (ej: archivo.pdf)
        """
        p = unquote(full_path)
        site_prefix = f"/sites/{SITE_PATH}/"

        if p.startswith(site_prefix):
            p = p[len(site_prefix):]

        if library_display_hint:
            hint = library_display_hint.rstrip("/") + "/"
            if p.lower().startswith(hint.lower()):
                p = p[len(hint):]
        else:
            parts = p.split("/", 1)
            if len(parts) == 2:
                p = parts[1]

        return p.lstrip("/")

    @classmethod
    def upload_file_to_sharepoint(
            cls,
            file_path: str,
            file_data: bytes,
            replace_existing: bool = True,
            verify_upload: bool = True
    ) -> Optional[str]:
        """
        Sube archivo a SharePoint usando Microsoft Graph API

        Args:
            file_path: Ruta del archivo en SharePoint (ej: "users/profile_photos/user_1.jpg")
            file_data: Contenido binario del archivo
            replace_existing: Si True, sobrescribe archivos existentes
            verify_upload: Si True, verifica que el archivo se subió correctamente

        Returns:
            URL completa del archivo en SharePoint o None si falla
        """
        try:
            logger.info(f"Subiendo archivo: {file_path} ({len(file_data)} bytes)")
            full_sharepoint_path = f"{file_path}"

            SharePointManager.get_config()
            # Verificar si existe (si no se permite reemplazar)
            if not replace_existing:
                try:
                    check_url = cls.build_graph_url(full_sharepoint_path)
                    check_response = requests.get(check_url, headers=cls.get_auth_headers())
                    if check_response.status_code == 200:
                        logger.warning(f"Archivo ya existe: {full_sharepoint_path}")
                        return None
                except:
                    pass  # Continuar si hay error verificando

            # Subir archivo

            upload_url = cls.build_graph_url(full_sharepoint_path, "/content")
            headers = {**cls.get_auth_headers(), 'Content-Type': 'application/octet-stream'}

            upload_response = requests.put(upload_url, headers=headers, data=file_data, timeout=120)

            if upload_response.status_code not in [200, 201]:
                logger.error(f"Error subiendo: {upload_response.status_code} - {upload_response.text}")
                return None

            logger.info("Archivo subido exitosamente")

            # Verificar subida
            if verify_upload:
                verify_url = cls.build_graph_url(full_sharepoint_path)
                verify_response = requests.get(verify_url, headers=cls.get_auth_headers())
                if verify_response.status_code != 200:
                    logger.error("Verificación falló: archivo no existe después de subir")
                    return None
                logger.info("VERIFICACIÓN: Archivo confirmado en SharePoint")

            # Construir URL completa
            full_url = f"{SHAREPOINT_SITE_URL}/{SHAREPOINT_DOC_LIB}/{file_path}"
            logger.info(f"URL del archivo: {full_url}")
            return full_url

        except Exception as e:
            logger.exception(f"Error subiendo archivo: {e}")
            return None

    @classmethod
    def delete_file_by_path(cls, file_path: str) -> bool:
        """
        Elimina archivo por ruta usando Graph API

        Args:
            file_path: Ruta del archivo (ej: "users/profile_photos/user_1.jpg")

        Returns:
            True si se eliminó o no existía, False si hubo error
        """
        try:
            delete_url = cls.build_graph_url(file_path)
            delete_response = requests.delete(delete_url, headers=cls.get_auth_headers())

            if delete_response.status_code in [204, 404]:
                logger.info(f"Archivo eliminado o no existía: {file_path}")
                return True
            else:
                logger.warning(f"Error eliminando {file_path}: {delete_response.status_code}")
                return False

        except Exception as e:
            logger.warning(f"Error eliminando {file_path}: {e}")
            return False

    @classmethod
    def get_file_content_from_sharepoint(
            cls,
            file_url: str,
            expected_content_type: str = None,
            timeout: int = 30
    ) -> Optional[Tuple[bytes, str]]:
        """
        Obtiene contenido de archivo desde SharePoint

        Args:
            file_url: URL completa del archivo en SharePoint
            expected_content_type: Tipo de contenido esperado (opcional)
            timeout: Timeout en segundos

        Returns:
            Tupla (contenido_bytes, content_type) o None si falla
        """
        try:
            # Procesar URL para obtener path relativo
            parsed = urlparse(file_url)
            lib_relative = cls.site_relative_to_library_relative(parsed.path, DOC_LIB_DISPLAY_NAME)

            # Obtener contenido
            content_url = cls.build_graph_url(lib_relative, "/content")
            headers = {**cls.get_auth_headers(), "Accept": "application/octet-stream"}

            response = requests.get(content_url, headers=headers, timeout=timeout)

            if response.status_code == 200:
                # Determinar content type
                content_type = response.headers.get('content-type', 'application/octet-stream')

                if content_type == 'application/octet-stream':
                    file_extension = Path(lib_relative).suffix[1:].lower()
                    content_type = cls.get_content_type_from_extension(file_extension)

                # Validar content type si se especificó
                if expected_content_type and not content_type.startswith(expected_content_type):
                    logger.warning(
                        f"Content type inesperado: esperado {expected_content_type}, obtenido {content_type}")

                logger.info(f"Archivo obtenido: {len(response.content)} bytes, tipo: {content_type}")
                return response.content, content_type

            elif response.status_code == 404:
                logger.warning(f"Archivo no encontrado: {lib_relative}")
                return None
            else:
                try:
                    error_details = response.json()
                except:
                    error_details = response.text

                logger.error(f"Error Graph API {response.status_code}: {error_details}")
                raise RuntimeError(f"Error {response.status_code} obteniendo archivo: {error_details}")

        except Exception as e:
            logger.exception(f"Error obteniendo archivo: {e}")
            return None

    @classmethod
    def get_content_type_from_extension(cls, file_extension: str) -> str:
        """
        Mapea extensiones de archivo a content types

        Args:
            file_extension: Extensión del archivo (sin punto)

        Returns:
            Content type MIME correspondiente
        """
        content_type_map = {
            'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
            'gif': 'image/gif', 'webp': 'image/webp', 'bmp': 'image/bmp',
            'pdf': 'application/pdf',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'ppt': 'application/vnd.ms-powerpoint',
            'txt': 'text/plain', 'csv': 'text/csv', 'json': 'application/json',
            'zip': 'application/zip', 'rar': 'application/x-rar-compressed',
            'mp4': 'video/mp4', 'avi': 'video/x-msvideo',
            'mp3': 'audio/mpeg', 'wav': 'audio/wav'
        }
        return content_type_map.get(file_extension.lower(), 'application/octet-stream')

    @classmethod
    def refresh_config(cls):
        """
        Fuerza renovación de configuración

        Returns:
            Nueva configuración actualizada
        """
        return cls.get_config(force_refresh=True)

    @classmethod
    def get_file_info(cls, file_path: str) -> Optional[dict]:
        """
        Obtiene información metadata de un archivo

        Args:
            file_path: Ruta del archivo

        Returns:
            Diccionario con información del archivo o None si no existe
        """
        try:
            info_url = cls.build_graph_url(file_path)
            response = requests.get(info_url, headers=cls.get_auth_headers())

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.info(f"Archivo no encontrado: {file_path}")
                return None
            else:
                logger.error(f"Error obteniendo info: {response.status_code}")
                return None

        except Exception as e:
            logger.exception(f"Error obteniendo información de archivo: {e}")
            return None

    @classmethod
    def list_folder_contents(cls, folder_path: str = "") -> Optional[list]:
        """
        Lista contenido de una carpeta

        Args:
            folder_path: Ruta de la carpeta (vacío para raíz)

        Returns:
            Lista de elementos en la carpeta o None si error
        """
        try:
            if folder_path:
                list_url = cls.build_graph_url(folder_path, "/children")
            else:
                config = cls.get_config()
                list_url = f"https://graph.microsoft.com/v1.0/sites/{config.site_id}/drives/{config.drive_id}/root/children"

            response = requests.get(list_url, headers=cls.get_auth_headers())

            if response.status_code == 200:
                return response.json().get('value', [])
            else:
                logger.error(f"Error listando carpeta: {response.status_code}")
                return None

        except Exception as e:
            logger.exception(f"Error listando carpeta: {e}")
            return None


def upload_file(folder_path: str, file_name: str, file_data: bytes):
    """
        Sube documento usando la función genérica

        Args:
            folder_path: Carpeta destino (ej: "documents/contracts")
            file_name: Nombre del archivo (ej: "contract_2025.pdf")
            file_data: Contenido binario del archivo
        """
    try:
        file_path = f"{folder_path}/{file_name}"

        return SharePointManager.upload_file_to_sharepoint(
            file_path=file_path,
            file_data=file_data,
            replace_existing=True,
            verify_upload=True
        )

    except Exception as e:
        logger.exception(f"Error subiendo documento: {e}")
        return None

def ensure_folder(ctx, parent_folder, folder_parts):
    current_folder = parent_folder

    for part in folder_parts:
        try:
            subfolder = current_folder.folders.get_by_url(part)
            subfolder.get().execute_query()
            current_folder = subfolder
        except Exception:
            current_folder = current_folder.folders.add(part)
            ctx.execute_query()

    # Asegúrate de que las propiedades estén cargadas
    current_folder.get().execute_query()
    return current_folder

def get_file_extension_pathlib(server_relative_path: str) -> str:
    """
    Obtener extensión usando pathlib
    """
    return Path(server_relative_path).suffix.lower()

def fetch_sharepoint_file(document_url: str):
    """
    Obtiene documento (PDF, Excel, Word, etc.) con información de tipo
    """
    try:
        return SharePointManager.get_file_content_from_sharepoint(
            file_url=document_url,
            timeout=60  # Más tiempo para documentos grandes
        )

    except Exception as e:
        logger.error(f"Error obteniendo documento: {e}")
        return None

def get_content_type_from_extension(file_extension: str) -> str:
        """
        Mapea extensiones de archivo a content types
        """
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'pdf': 'application/pdf',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'txt': 'text/plain',
            'csv': 'text/csv',
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed'
        }

        return content_type_map.get(file_extension.lower(), 'application/octet-stream')



