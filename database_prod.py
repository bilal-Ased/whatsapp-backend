from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL connection string
DATABASE_URL = "postgresql://root:WU54ELDL0VKkFgkXmpKLhb76EtRYqpra@dpg-d10tlqili9vc73866uq0-a.oregon-postgres.render.com/silverfox_db"

# Create engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for models
Base = declarative_base()
