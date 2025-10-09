from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+psycopg2://koyeb-adm:npg_yIbzBjaF0O3c@ep-spring-resonance-a2qapsrq.eu-central-1.pg.koyeb.app:5432/koyebdb"

# Create the SQLAlchemy engine with proper connection handling
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    },
    pool_pre_ping=True,      # Test connections before using them
    pool_recycle=3600,       # Recycle connections every hour
    pool_size=5,             # Number of connections to keep openx
    max_overflow=10,         # Max additional connections
)

# Define Base for models
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)