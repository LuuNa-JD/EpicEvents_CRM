import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

engine = create_engine(settings.DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
