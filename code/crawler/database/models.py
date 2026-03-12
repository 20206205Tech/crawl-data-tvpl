from sqlalchemy import Column, DateTime, Index, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Raw(Base):
    __tablename__ = 'raw'

    item_id = Column(Integer, primary_key=True) 
    # Thêm thông tin bản ghi có file pdf hay không
    has_pdf = Column(Boolean, default=False)

    crawl_detail_started_at = Column(DateTime, nullable=True)
    crawl_detail_ended_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index(
            'ix_raw_pending_detail',
            'item_id',
            postgresql_where=(crawl_detail_started_at.is_(None))
        ),
        Index(
            'ix_raw_in_progress_detail',
            'crawl_detail_started_at',
            postgresql_where=(
                (crawl_detail_started_at.isnot(None)) & 
                (crawl_detail_ended_at.is_(None))
            )
        ),
    )