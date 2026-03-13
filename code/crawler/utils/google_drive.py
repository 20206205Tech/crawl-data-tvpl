import os
import json
from loguru import logger
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_drive_service():
    creds = None

    # 1. Ưu tiên đọc Token từ biến môi trường (GitHub Secrets)
    token_json = os.getenv('GOOGLE_DRIVE_TOKEN')

    if token_json:
        logger.info("Đang sử dụng Token từ Secrets...")
        creds_info = json.loads(token_json)
        creds = Credentials.from_authorized_user_info(creds_info, SCOPES)

    # 2. Đọc từ file token.json nếu chạy ở máy cá nhân
    elif os.path.exists('token.json'):
        logger.info("Đang sử dụng file token.json tại local...")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Tự động làm mới token nếu đã hết hạn
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            logger.error(f"Không thể refresh token: {e}")
            creds = None

    if not creds:
        raise Exception(
            "Không tìm thấy thông tin xác thực! Hãy chạy lấy token tại local trước.")

    return build('drive', 'v3', credentials=creds)


def upload_to_drive(service, file_path, folder_id):
    try:
        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        media = MediaFileUpload(
            file_path, mimetype='text/html', resumable=True)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        logger.debug(
            f"File uploaded: {file_name} | URL: https://drive.google.com/file/d/{file.get('id')}/view")

        return True
    except Exception as e:
        logger.error(f"Lỗi khi upload file {file_path}: {e}")
        return False
