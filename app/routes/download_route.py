from flask import Blueprint, request, jsonify, send_file
from services.sharepoint_service import get_access_token, download_sharepoint_file
import os

download_bp = Blueprint('download_bp', __name__)

@download_bp.route('/download-sharepoint', methods=['POST'])
def download_file():
    data = request.get_json()
    file_url = data.get('url')
    if not file_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        token = get_access_token()
        local_path = download_sharepoint_file(file_url, token)
        return send_file(local_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'local_path' in locals() and os.path.exists(local_path):
            os.remove(local_path)