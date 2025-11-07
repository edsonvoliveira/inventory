from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# file path SQLite database
DATABASE_URL = "sqlite:///backend/data/inventory.db"

# create connection engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# manager sessions connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for models
Base = declarative_base()