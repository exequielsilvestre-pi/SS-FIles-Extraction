import requests
import tempfile
import base64
from flask import current_app

def get_access_token():
    client_id = current_app.config['CLIENT_ID']
    client_secret = current_app.config['CLIENT_SECRET']
    tenant_id = current_app.config['TENANT_ID']

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        'client_id': client_id,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def encode_share_url(url):
    base64_url = base64.urlsafe_b64encode(url.encode()).decode()
    return base64_url.rstrip('=')

def download_sharepoint_file(file_url, token):
    headers = {'Authorization': f'Bearer {token}'}

    metadata_url = f"https://graph.microsoft.com/v1.0/shares/u!{encode_share_url(file_url)}/driveItem"
    metadata_resp = requests.get(metadata_url, headers=headers)
    metadata_resp.raise_for_status()
    item = metadata_resp.json()

    download_url = f"https://graph.microsoft.com/v1.0/drives/{item['parentReference']['driveId']}/items/{item['id']}/content"
    download_resp = requests.get(download_url, headers=headers, stream=True)
    download_resp.raise_for_status()

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    for chunk in download_resp.iter_content(chunk_size=8192):
        temp_file.write(chunk)
    temp_file.close()
    return temp_file.name
