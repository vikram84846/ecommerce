from sqlalchemy import create_engine
from sqlalchemy.orm import  sessionmaker
from core.config import app_settings



engine = create_engine(url=app_settings.DB_URL,echo=True)

SessionLocal = sessionmaker(engine,autoflush=True,autocommit=False)


