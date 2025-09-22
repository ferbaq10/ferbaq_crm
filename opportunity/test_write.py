from sharepoint import SharePointManager
import requests

def test_write_permissions():
    """Probar si realmente tiene permisos de escritura"""
    try:
        config = SharePointManager.get_config(force_refresh=True)
        headers = {'Authorization': f'Bearer {config.token}'}

        # Probar crear una carpeta (operación de escritura)
        test_url = f"https://graph.microsoft.com/v1.0/sites/{config.site_id}/drives/{config.drive_id}/root/children"

        test_folder = {
            "name": "test_permissions_folder",
            "folder": {}
        }

        response = requests.post(test_url, json=test_folder, headers=headers)

        if response.status_code == 201:
            print("✓ Permisos de escritura FUNCIONANDO")
            # Limpiar - eliminar carpeta de prueba
            delete_url = f"https://graph.microsoft.com/v1.0/sites/{config.site_id}/drives/{config.drive_id}/root:/test_permissions_folder"
            requests.delete(delete_url, headers=headers)
        elif response.status_code == 403:
            print("✗ Sin permisos de escritura")
        else:
            print(f"Respuesta inesperada: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error probando permisos: {e}")