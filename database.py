import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise ValueError("SUPABASE_DB_URL not found in .env file. Please add it to continue.")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
