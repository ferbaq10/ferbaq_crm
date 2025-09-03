import io
import logging
import os
from pathlib import Path
from urllib.parse import urlparse, unquote

from decouple import config
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.folders.folder import Folder

SHAREPOINT_SITE_URL = config("SHAREPOINT_SITE_URL")
SHAREPOINT_DOC_LIB = config("SHAREPOINT_DOC_LIB", "Biblioteca de Documentos")
SHAREPOINT_USERNAME = config("SHAREPOINT_USERNAME")
SHAREPOINT_PASSWORD = config("SHAREPOINT_PASSWORD")

logger = logging.getLogger(__name__)

def _get_ctx() -> ClientContext:
    ctx_auth = AuthenticationContext(SHAREPOINT_SITE_URL)
    ok = ctx_auth.acquire_token_for_user(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD)
    if not ok:
        raise Exception("Autenticación con SharePoint fallida (User/Pass).")
    return ClientContext(SHAREPOINT_SITE_URL, ctx_auth)

def upload_file(path: str, file_data: bytes):
    try:
        ctx = _get_ctx()

        # 2. Separar ruta y archivo
        folder_path = os.path.dirname(path).strip("/")
        file_name = os.path.basename(path)
        folder_parts = folder_path.split("/")

        # 3. Ir al folder raíz
        site_path = urlparse(SHAREPOINT_SITE_URL).path.strip("/")
        root_relative_url = f"/{site_path}/{SHAREPOINT_DOC_LIB.strip()}"
        root_folder = ctx.web.get_folder_by_server_relative_url(root_relative_url)

        # 4. Crear subcarpetas si no existen
        target_folder: Folder = ensure_folder(ctx, root_folder, folder_parts)

        # 5. Subir archivo (eliminar primero si existe)
        file_stream = io.BytesIO(file_data)

        try:
            existing_file = target_folder.files.get_by_url(file_name)
            existing_file.delete_object()
            ctx.execute_query()
        except Exception:
            logger.info(f"ℹ️ El archivo '{file_name}' no existía, no fue necesario eliminarlo.")

        target_folder.get().execute_query()
        uploaded_file = target_folder.upload_file(file_name, file_stream).execute_query()

        # 6. Confirmación
        logger.info(f"Archivo subido correctamente a SharePoint: {uploaded_file.serverRelativeUrl}")
        return uploaded_file.serverRelativeUrl

    except Exception as e:
        logger.exception(f"Error al subir archivo a SharePoint: {e}")
        raise

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

def _delete_file_from_sharepoint(full_url: str):
    parsed = urlparse(full_url)
    relative_url = unquote(parsed.path)  # /sites/CRM_PRUEBA/Documentos compartidos/...

    ctx = _get_ctx()
    file = ctx.web.get_file_by_server_relative_url(relative_url)
    file.delete_object()
    ctx.execute_query()


def get_file_extension_pathlib(server_relative_path: str) -> str:
    """
    Obtener extensión usando pathlib
    """
    return Path(server_relative_path).suffix.lower()

def fetch_sharepoint_file(sharepoint_url: str):
    """
    Recuperar imagen de sharepoint
    """
    try:
        ctx = _get_ctx()

        from urllib.parse import urlparse, unquote
        parsed = urlparse(sharepoint_url)
        server_relative_path = unquote(parsed.path)

        # Metodo DIRECTO usando open_binary (recomendado)
        from office365.sharepoint.files.file import File
        response = File.open_binary(ctx, server_relative_path)

        if response.status_code == 200:
            file_extension: str = get_file_extension_pathlib(server_relative_path)
            return response.content, f"image/{file_extension}"
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise