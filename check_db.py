import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        print(f"Connection successful. User count: {result.fetchone()[0]}")
        
        # Check sessions
        result = conn.execute(text("SELECT COUNT(*) FROM chat_sessions"))
        print(f"Chat session count: {result.fetchone()[0]}")
        
        # Check profiles
        result = conn.execute(text("SELECT COUNT(*) FROM student_profiles"))
        print(f"Student profile count: {result.fetchone()[0]}")

except Exception as e:
    print(f"Connection failed: {e}")
