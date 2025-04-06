# create_tables.py
from sqlalchemy import create_engine
from models import Base  # Import your Base from the models.py
from database import DATABASE_URL  # Assuming you have DATABASE_URL setup in database.py

# Initialize engine with the database URL
engine = create_engine(DATABASE_URL)

# Create tables in the database
Base.metadata.create_all(engine)

print("Tables created successfully!")
