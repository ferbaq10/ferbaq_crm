import logging
import re
import unicodedata
from urllib.parse import quote
from urllib.parse import urljoin, urlparse

from decouple import config
from django_rq import job

from opportunity.models import OpportunityDocument, Opportunity
from opportunity.sharepoint import upload_file, delete_document

logger = logging.getLogger(__name__)
SHAREPOINT_SITE_URL = config("SHAREPOINT_SITE_URL")


# =========================================================
# UTILIDADES DE SANITIZACIÓN
# =========================================================

def sanitize_folder_name(value: str) -> str:
    if not value:
        return "SIN_NOMBRE"

    # Quitar acentos
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")

    # Reemplazar caracteres inválidos para Windows / SharePoint
    value = re.sub(r'[<>:"/\\|?*]', '-', value)

    # Reemplazar guiones largos unicode por normal
    value = value.replace("–", "-").replace("—", "-")

    # Quitar espacios múltiples
    value = re.sub(r"\s+", " ", value)

    # Quitar espacios y puntos al final
    value = value.strip().rstrip(".")

    return value


# =========================================================
# UPLOAD
# =========================================================

@job
def upload_to_sharepoint_db(udn: str, opportunity_id: int, file_data: bytes, file_name: str):
    try:
        opportunity = Opportunity.objects.select_related(
            "project"
        ).get(id=opportunity_id)

        project_name = sanitize_folder_name(opportunity.project.name)
        opportunity_name = sanitize_folder_name(opportunity.name)
        requisition = sanitize_folder_name(opportunity.requisition_number or "SIN_REQ")
        udn = sanitize_folder_name(udn)

        file_name = sanitize_folder_name(file_name[:255])

        folder_name = (
            f"COMERCIAL/WORKSPACE/"
            f"{udn}/"
            f"{project_name}/"
            f"{requisition}_{opportunity_name}"
        )

        relative_url = upload_file(folder_name, file_name, file_data)

        full_url = build_sharepoint_url(SHAREPOINT_SITE_URL, relative_url)
        full_url = quote(full_url, safe=':/')

        OpportunityDocument.objects.update_or_create(
            opportunity=opportunity,
            file_name=file_name,
            defaults={"sharepoint_url": full_url},
        )

        logger.info(
            f"Archivo subido correctamente: {file_name} → {full_url}"
        )

    except Exception as e:
        logger.exception(f"Fallo al subir archivo para oportunidad: {e}")


# =========================================================
# URL BUILDER
# =========================================================

def build_sharepoint_url(base_url: str, relative_url: str) -> str:
    base_path = urlparse(base_url).path.rstrip('/')
    relative_clean = relative_url

    if relative_url.startswith(base_path):
        relative_clean = relative_url[len(base_path):]

    return urljoin(base_url + '/', relative_clean.lstrip('/'))


# =========================================================
# DELETE
# =========================================================

def delete_file_from_sharepoint_db(full_url: str, doc_id):
    try:
        result_delete = delete_document(full_url)
        if result_delete:
            logger.info(f"Archivo eliminado de SharePoint: {full_url}")
            OpportunityDocument.objects.filter(id=doc_id).delete()
            logger.info(f"Registro OpportunityDocument eliminado: ID={doc_id}")
    except Exception as e:
        logger.warning(f"Error al eliminar archivo en SharePoint: {e}.")
