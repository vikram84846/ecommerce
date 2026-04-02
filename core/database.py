from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from core.config import get_settings

app_settings = get_settings()

engine = create_async_engine(
    url=str(app_settings.DB_URL),
    echo=app_settings.DEBUG,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(engine)