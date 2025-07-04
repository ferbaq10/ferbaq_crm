import io
import logging
import os
from urllib.parse import urlparse, unquote

from decouple import config
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.folders.folder import Folder

# Cargar tus credenciales (idealmente desde variables de entorno)
SHAREPOINT_SITE_URL = config("SHAREPOINT_SITE_URL")
SHAREPOINT_DOC_LIB = config("SHAREPOINT_DOC_LIB", "Documentos compartidos")
SHAREPOINT_USERNAME = config("SHAREPOINT_USERNAME")
SHAREPOINT_PASSWORD = config("SHAREPOINT_PASSWORD")

logger = logging.getLogger(__name__)

def upload_file(path: str, file_data: bytes):
    try:
        # 1. Autenticación con SharePoint
        ctx_auth = AuthenticationContext(SHAREPOINT_SITE_URL)
        if not ctx_auth.acquire_token_for_user(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD):
            raise Exception("Autenticación con SharePoint fallida")

        ctx = ClientContext(SHAREPOINT_SITE_URL, ctx_auth)

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

        print("DEBUG - Folder URL:", target_folder.properties.get("ServerRelativeUrl"))
        target_folder.get().execute_query()
        uploaded_file = target_folder.upload_file(file_name, file_stream).execute_query()

        # 6. Confirmación
        logger.info(f"✅ Archivo subido correctamente a SharePoint: {uploaded_file.serverRelativeUrl}")
        return uploaded_file.serverRelativeUrl

    except Exception as e:
        logger.exception(f"❌ Error al subir archivo a SharePoint: {e}")
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

    # ✅ Asegúrate de que las propiedades estén cargadas
    current_folder.get().execute_query()
    return current_folder


def _delete_file_from_sharepoint(full_url: str):
    parsed = urlparse(full_url)
    relative_url = unquote(parsed.path)  # /sites/CRM_PRUEBA/Documentos compartidos/...

    ctx_auth = AuthenticationContext(SHAREPOINT_SITE_URL)
    if not ctx_auth.acquire_token_for_user(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD):
        raise Exception("Autenticación con SharePoint fallida")

    ctx = ClientContext(SHAREPOINT_SITE_URL, ctx_auth)
    file = ctx.web.get_file_by_server_relative_url(relative_url)
    file.delete_object()
    ctx.execute_query()