from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import os
import io
import logging

# Cargar tus credenciales (idealmente desde variables de entorno)
SHAREPOINT_SITE_URL = os.getenv("SHAREPOINT_SITE_URL")
SHAREPOINT_DOC_LIB = os.getenv("SHAREPOINT_DOC_LIB", "Documentos compartidos")
SHAREPOINT_USERNAME = os.getenv("SHAREPOINT_USERNAME")
SHAREPOINT_PASSWORD = os.getenv("SHAREPOINT_PASSWORD")

logger = logging.getLogger(__name__)

def upload_file(path: str, file_data: bytes):
    try:
        ctx_auth = AuthenticationContext(SHAREPOINT_SITE_URL)
        if not ctx_auth.acquire_token_for_user(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD):
            raise Exception("Autenticación con SharePoint fallida")

        ctx = ClientContext(SHAREPOINT_SITE_URL, ctx_auth)
        target_folder = ctx.web.get_folder_by_server_relative_url(SHAREPOINT_DOC_LIB + path)

        # Asegúrate de que la carpeta exista (si no, SharePoint falla)
        try:
            target_folder.get().execute_query()
        except Exception:
            # Crear carpeta si no existe
            parent_folder = ctx.web.get_folder_by_server_relative_url(SHAREPOINT_DOC_LIB)
            parent_folder.folders.add(path).execute_query()
            target_folder = ctx.web.get_folder_by_server_relative_url(SHAREPOINT_DOC_LIB + path)

        file_stream = io.BytesIO(file_data)
        file_name = os.path.basename(path)

        uploaded_file = target_folder.upload_file(file_name, file_stream).execute_query()

        logger.info(f"Archivo subido a SharePoint: {uploaded_file.serverRelativeUrl}")
        return uploaded_file.serverRelativeUrl

    except Exception as e:
        logger.exception(f"Error al subir archivo a SharePoint: {e}")
        raise
