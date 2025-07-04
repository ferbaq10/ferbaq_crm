import logging

from django_rq import job

from opportunity.sharepoint import upload_file

logger = logging.getLogger(__name__)

@job
def upload_to_sharepoint(udn: str, opportunity_name: str, file_data: bytes, file_name: str):
    try:
        sharepoint_path = f"/{udn}/opportunities/{opportunity_name}"
        full_path = f"{sharepoint_path}/{file_name}"

        url = upload_file(full_path, file_data)

        logger.info(f"Archivo de oportunidad {opportunity_name} subido a SharePoint en {url}")
        # Aquí podrías registrar la URL en tu modelo si quieres

    except Exception as e:
        logger.exception(f"Fallo al subir archivo para oportunidad {opportunity_name}: {e}")
