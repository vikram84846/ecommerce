from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from core.config import app_settings


engine = create_async_engine(app_settings.database_url, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
