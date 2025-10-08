from database import engine, Base
import models
import traceback

def create_tables():
    try:
        print("Creating database tables using SQLAlchemy...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    create_tables()
