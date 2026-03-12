import scrapy
import os
from loguru import logger
from crawler.env import CRAWL_DATA_ENV_DEV, PATH_FOLDER_DATA
from crawler.database.config import session_scope
from crawler.database.service import RawService

class DocumentDetailSpider(scrapy.Spider):
    name = "document_detail"
    allowed_domains = ["files.thuvienphapluat.vn"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(PATH_FOLDER_DATA, exist_ok=True)

    def start_requests(self):
        limit = 20 if CRAWL_DATA_ENV_DEV else 100
        
        with session_scope() as db_session:
            service = RawService(db_session)
            item_ids = service.fetch_pending_details(limit=limit)

        if not item_ids:
            logger.info("🏁 Không còn bản ghi nào cần crawl.")
            return

        for item_id in item_ids:
            pdf_url = f"https://files.thuvienphapluat.vn/uploads/FilePDFUpload/{item_id}.pdf"
            yield scrapy.Request(
                url=pdf_url,
                callback=self.save_pdf,
                meta={'item_id': item_id, 'handle_httpstatus_list': [404]}
            )

    def save_pdf(self, response):
        item_id = response.meta['item_id']

        # 1. Xử lý lỗi 404
        if response.status == 404:
            logger.warning(f"⏩ ID {item_id}: 404 Not Found - Bỏ qua.")
            yield {
                'item_id': item_id,
                'status': '404_not_found',
                'file_path': None
            }
            return

        # 2. Lưu file PDF nếu thành công
        file_name = f"{item_id}.pdf"
        file_path = os.path.join(PATH_FOLDER_DATA, file_name)
        
        try:
            if b'%PDF' in response.body[:10]:
                with open(file_path, 'wb') as f:
                    f.write(response.body)
                
                logger.success(f"💾 Đã tải thành công: {file_name}")
                
                # Yield data để ghi vào file jsonl
                yield {
                    'item_id': item_id,
                    'status': 'success',
                    'file_path': file_path
                }
            else:
                logger.error(f"❌ ID {item_id} không phải định dạng PDF.")
                yield {
                    'item_id': item_id,
                    'status': 'invalid_format',
                    'file_path': None
                }
        except Exception as e:
            logger.error(f"❌ Lỗi lưu file {item_id}: {e}")