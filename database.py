from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL connection string
DATABASE_URL = "mysql+pymysql://bilal:Bilal%402025@127.0.0.1:3306/banking_crm"

# Create engine
engine = create_engine(
    DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()





