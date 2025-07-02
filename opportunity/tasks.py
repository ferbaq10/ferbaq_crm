from django_rq import job
from opportunity.sharepoint import upload_file
import logging

logger = logging.getLogger(__name__)

@job
def upload_to_sharepoint(opportunity_id: int, file_data: bytes, file_name: str):
    try:
        sharepoint_path = f"/opportunities/{opportunity_id}"
        full_path = f"{sharepoint_path}/{file_name}"

        url = upload_file(full_path, file_data)

        logger.info(f"Archivo de oportunidad {opportunity_id} subido a SharePoint en {url}")
        # Aquí podrías registrar la URL en tu modelo si quieres

    except Exception as e:
        logger.exception(f"Fallo al subir archivo para oportunidad {opportunity_id}: {e}")
