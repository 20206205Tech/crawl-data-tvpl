from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
from datetime import datetime, timedelta
from loguru import logger
from .models import Raw

class RawService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_pending_details(self, limit=10):
        """Lấy item_id chưa crawl, nếu thiếu sẽ tự sinh thêm ID mới từ max(id) + 1"""
        try:
            # 1. Kiểm tra xem hiện tại có bao nhiêu bản ghi chưa crawl
            pending_stmt = select(Raw.item_id).where(Raw.crawl_detail_started_at.is_(None)).limit(limit)
            pending_ids = self.db.execute(pending_stmt).scalars().all()

            # 2. Nếu thiếu bản ghi, tiến hành sinh thêm
            if len(pending_ids) < limit:
                needed = limit - len(pending_ids)
                
                # Tìm ID lớn nhất hiện tại
                max_id_stmt = select(func.max(Raw.item_id))
                current_max = self.db.execute(max_id_stmt).scalar() or 0
                
                new_items = []
                for i in range(1, needed + 1):
                    new_id = current_max + i
                    new_items.append(Raw(item_id=new_id))
                
                self.db.add_all(new_items)
                self.db.flush() 
                logger.info(f"✨ Đã tự động sinh thêm {needed} ID mới (từ {current_max + 1} đến {current_max + needed})")

            # 3. Thực hiện lấy và đánh dấu 'started_at' (Atomic update)
            subquery = (
                select(Raw.item_id)
                .where(Raw.crawl_detail_started_at.is_(None))
                .limit(limit)
                .with_for_update(skip_locked=True)
                .scalar_subquery()
            )

            stmt = (
                update(Raw)
                .where(Raw.item_id.in_(subquery))
                .values(crawl_detail_started_at=datetime.now())
                .returning(Raw.item_id)
            )

            result = self.db.execute(stmt)
            rows = result.scalars().all()
            self.db.commit()
            return rows
            
        except Exception as e:
            logger.error(f"❌ Lỗi fetch_pending_details: {e}")
            self.db.rollback()
            return []

    def mark_details_completed(self, item_id: int, has_pdf: bool = False):
        """Cập nhật trạng thái hoàn thành và xác nhận có PDF hay không"""
        try:
            self.db.execute(
                update(Raw)
                .where(Raw.item_id == item_id)
                .values(
                    crawl_detail_ended_at=datetime.now(),
                    has_pdf=has_pdf
                )
            )
            self.db.commit()
            # logger.debug(f"✅ Cập nhật hoàn tất ID {item_id} (PDF: {has_pdf})")
        except Exception as e:
            logger.error(f"Lỗi cập nhật kết quả cho ID {item_id}: {e}")
            self.db.rollback()

    # def release_stuck_tasks(self, hours_stuck: int = 12):
    #     """
    #     Giải phóng các bản ghi bị kẹt:
    #     - Đã có started_at nhưng chưa có ended_at
    #     - Thời gian bắt đầu đã trôi qua hơn hours_stuck
    #     """
    #     try:
    #         threshold_time = datetime.now() - timedelta(hours=hours_stuck)
            
    #         stmt = (
    #             update(Raw)
    #             .where(
    #                 Raw.crawl_detail_started_at.isnot(None),
    #                 Raw.crawl_detail_ended_at.is_(None),
    #                 Raw.crawl_detail_started_at <= threshold_time
    #             )
    #             .values(crawl_detail_started_at=None) # Reset để crawl lại
    #         )
            
    #         result = self.db.execute(stmt)
    #         self.db.commit()
            
    #         released_count = result.rowcount
    #         if released_count > 0:
    #             logger.success(f"🔄 Đã giải phóng {released_count} bản ghi bị kẹt quá {hours_stuck} giờ.")
    #         return released_count
            
    #     except Exception as e:
    #         logger.error(f"❌ Lỗi khi giải phóng task bị kẹt: {e}")
    #         self.db.rollback()
    #         return 0