from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from core.config import get_settings
from models.base import Base
app_settings = get_settings()

engine = create_async_engine(
    url=str(app_settings.DB_URL),
    echo=app_settings.DEBUG,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(engine)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)