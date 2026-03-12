from loguru import logger
from crawler.database.config import session_scope
from crawler.database.service import RawService

def main():
    logger.info("Bắt đầu quét và giải phóng các bản ghi kẹt...")
    with session_scope() as db_session:
        service = RawService(db_session)
        service.release_stuck_tasks(hours_stuck=12)

if __name__ == "__main__":
    main()