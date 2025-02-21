from sqlalchemy import create_engine
from models import Base
from database import SQLALCHEMY_DATABASE_URL
import os

def init_database():
    # Create the database directory if it doesn't exist
    db_dir = os.path.dirname(SQLALCHEMY_DATABASE_URL.replace('sqlite:///', ''))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()