from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+psycopg2://koyeb-adm:npg_yIbzBjaF0O3c@ep-spring-resonance-a2qapsrq.eu-central-1.pg.koyeb.app:5432/koyebdb"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Define Base for models
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
