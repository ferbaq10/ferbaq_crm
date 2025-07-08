import logging
from urllib.parse import quote
from urllib.parse import urljoin, urlparse

from decouple import config
from django_rq import job

from opportunity.models import OpportunityDocument, Opportunity
from opportunity.sharepoint import upload_file, _delete_file_from_sharepoint

logger = logging.getLogger(__name__)
SHAREPOINT_SITE_URL = config("SHAREPOINT_SITE_URL")

@job
def upload_to_sharepoint_db(udn: str, opportunity_id: int, file_data: bytes, file_name: str):
    try:
        opportunity = Opportunity.objects.get(pk=opportunity_id)
        sharepoint_path = f"/{udn}/opportunities/{opportunity.name}"
        full_path = f"{sharepoint_path}/{file_name}"

        relative_url = upload_file(full_path, file_data)
        full_url = build_sharepoint_url(SHAREPOINT_SITE_URL, relative_url)
        full_url = quote(full_url, safe=':/')

        OpportunityDocument.objects.update_or_create(
            opportunity=opportunity,
            file_name=file_name,
            sharepoint_url=full_url,
        )

        logger.info(f"Archivo de oportunidad {opportunity.name} subido a SharePoint en {full_url}")
        # Aquí podrías registrar la URL en tu modelo si quieres

    except Exception as e:
        logger.exception(f"Fallo al subir archivo para oportunidad: {e}")

def build_sharepoint_url(base_url: str, relative_url: str) -> str:
    base_path = urlparse(base_url).path.rstrip('/')
    relative_clean = relative_url

    if relative_url.startswith(base_path):
        relative_clean = relative_url[len(base_path):]

    return urljoin(base_url + '/', relative_clean.lstrip('/'))


@job
def delete_file_from_sharepoint_db(full_url: str, doc_id):
    try:
        _delete_file_from_sharepoint(full_url)
        logger.info(f"Archivo eliminado de SharePoint: {full_url}")
        OpportunityDocument.objects.filter(id=doc_id).delete()
        logger.info(f"🗑️ Registro OpportunityDocument eliminado: ID={doc_id}")
    except Exception as e:
        logger.warning(f"Error al eliminar archivo en SharePoint: {e}.")


