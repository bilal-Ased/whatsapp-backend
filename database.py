# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# MySQL Connection URL
DATABASE_URL = "mysql+pymysql://bilal:Bilal%402025@127.0.0.1:3306/whatsapp_db"

# Create engine
engine = create_engine(DATABASE_URL)

# Session local (for FastAPI requests)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from models import Base
    Base.metadata.create_all(bind=engine)
