from core.database import SessionLocal

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


get_db()