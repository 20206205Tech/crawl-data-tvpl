import os
from environs import Env
from loguru import logger


env = Env()
logger.info(f"Loading environment variables...")


PATH_FILE_CODE = os.path.abspath(__file__)
PATH_FOLDER_CODE = os.path.dirname(PATH_FILE_CODE)
PATH_FOLDER_DATA = os.path.join(PATH_FOLDER_CODE, "../../data")

CRAWL_DATA_ENV_DEV = env.bool("CRAWL_DATA_ENV_DEV", default=False)


CRAWL_DATA_TVPL_DATABASE_URL = env.str("CRAWL_DATA_TVPL_DATABASE_URL")



PATH_FILE_DOCUMENT_DETAIL = os.path.join(PATH_FOLDER_DATA, "document_detail.jsonl")
