from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:welcome@localhost:5432/career_guidance_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)