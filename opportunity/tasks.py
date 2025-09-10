import logging
from urllib.parse import quote
from urllib.parse import urljoin, urlparse

from decouple import config
from django_rq import job

from opportunity.models import OpportunityDocument, Opportunity
from opportunity.sharepoint import upload_file, delete_document

logger = logging.getLogger(__name__)
SHAREPOINT_SITE_URL = config("SHAREPOINT_SITE_URL")

@job
def upload_to_sharepoint_db(udn: str, opportunity_id: int, file_data: bytes, file_name: str):
    try:
        # Hay que volver a obtener el objeto opportunity porque no se puede pasar como parametro el objeto
        opportunity = Opportunity.objects.get(id=opportunity_id)
        project_name = opportunity.project.name
        file_name = file_name[:255] # Solo hasta 200 caracteres
        folder_name = f"COMERCIAL/WORKSPACE/{udn}/{project_name}/{opportunity.requisition_number}_{opportunity.name}"

        relative_url = upload_file(folder_name, file_name, file_data)
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


def delete_file_from_sharepoint_db(full_url: str, doc_id):
    try:
        result_delete = delete_document(full_url)
        if result_delete:
            logger.info(f"Archivo eliminado de SharePoint: {full_url}")
            OpportunityDocument.objects.filter(id=doc_id).delete()
            logger.info(f"Registro OpportunityDocument eliminado: ID={doc_id}")
    except Exception as e:
        logger.warning(f"Error al eliminar archivo en SharePoint: {e}.")


