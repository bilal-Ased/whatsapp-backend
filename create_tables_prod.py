from database_prod import engine, Base
import models_prod  # Make sure this imports your SQLAlchemy models
import traceback
from sqlalchemy import text

def test_connection():
    print("Testing PostgreSQL connection via SQLAlchemy...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Connection test passed:", list(result))
    except Exception as conn_error:
        print("PostgreSQL connection failed.")
        print(traceback.format_exc())
        raise conn_error

def create_tables():
    try:
        test_connection()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating tables: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    create_tables()
