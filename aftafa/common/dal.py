"""
Data Access Layer
"""
import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from aftafa.common.config import Config


logging.basicConfig()

config: Config = Config()
postgres_url = config.postgres_url
db_logs_path: Path = Path(config.configs.get('logging').get('database_logs_path'))

db_logger = logging.getLogger('sqlalchemy.engine')
db_handler = logging.FileHandler(db_logs_path)
db_handler.setLevel(logging.DEBUG)
db_logger.addHandler(db_handler)

engine = create_engine(url=postgres_url)
session = Session(bind=engine)
