import os
import json
from loguru import logger
from crawler.database.config import session_scope
from crawler.database.service import RawService
from crawler.env import PATH_FOLDER_DATA
from crawler.env import PATH_FILE_DOCUMENT_DETAIL
from crawler.utils.google_drive import get_drive_service, upload_to_drive

CRAWL_DATA_TVPL_GOOGLE_DRIVE_PDF_FOLDER_ID = os.getenv(
    'CRAWL_DATA_TVPL_GOOGLE_DRIVE_PDF_FOLDER_ID')


def main():
    if not os.path.exists(PATH_FILE_DOCUMENT_DETAIL):
        logger.error(
            f"Không tìm thấy file danh sách: {PATH_FILE_DOCUMENT_DETAIL}")
        return

    try:
        service_drive = get_drive_service()

        with open(PATH_FILE_DOCUMENT_DETAIL, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                item_id = data.get('item_id')
                status = data.get('status')
                file_path = data.get('file_path')

                has_pdf = False

                # Nếu cào thành công và có file trên đĩa
                if status == 'success' and file_path and os.path.exists(file_path):
                    logger.info(f"📤 Đang upload ID {item_id} lên Drive...")
                    if upload_to_drive(service_drive, file_path, CRAWL_DATA_TVPL_GOOGLE_DRIVE_PDF_FOLDER_ID):
                        has_pdf = True
                        # Tùy chọn: os.remove(file_path) # Xóa sau khi upload thành công
                    else:
                        logger.error(f"❌ Upload thất bại cho ID {item_id}")

                # Cập nhật trạng thái cuối cùng vào Database
                with session_scope() as db_session:
                    db_service = RawService(db_session)
                    db_service.mark_details_completed(item_id, has_pdf=has_pdf)

                logger.success(
                    f"✔️ Hoàn tất xử lý ID: {item_id} (Has PDF: {has_pdf})")

    except Exception as e:
        logger.critical(f"Lỗi quy trình load dữ liệu: {e}")


if __name__ == "__main__":
    main()
