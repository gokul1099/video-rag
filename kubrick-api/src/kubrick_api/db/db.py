from sqlalchemy import create_engine, event
from sqlalchemy.orm import (
    sessionmaker,
    Session,
    declarative_base
)
import logging
from typing import Generator
from kubrick_api.config import get_settings
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):            
        self.settings = get_settings()
        self.engine = None
        self.session_local = None
        self.Base = declarative_base()
        self._initialize()

    def _initialize(self):
        """Create engine with error handling"""
        try:
            self.engine = create_engine(
            self.settings.DATABASE_URL,
            echo=False,
            pool_size=self.settings.DB_POOL_SIZE,
            max_overflow=10,
            pool_pre_ping=self.settings.DB_POOL_PRE_PING,
            pool_recycle=3600
            )
            self.session_local = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"failed to initialize database {e}")
            raise

    def get_session(self) -> Generator[Session, None, None]:
        db = self.session_local()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database session error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    

    def init_db(self):
        try:
            self.Base.metadata.create_all(bind=self.engine)
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def drop_all_tables(self):
        try:
            self.Base.metadata.drop_all(bind=self.engine)
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")

    def shutdown(self):
        """Properly dispose of engine on app shutdown"""
        if self.engine:
            try:
                self.engine.dispose()
                logger.info("Database engine disposed")
            except Exception as e:
                logger.error(f"Error disposing engine :{e}")

_db_manager: Optional[DatabaseManager] = None

def get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def get_db() -> Generator[Session, None, None]:
    db_manager = get_db_manager()
    yield from db_manager.get_session()
