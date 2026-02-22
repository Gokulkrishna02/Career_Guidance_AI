import os
from sqlalchemy import text
from database import SessionLocal, engine
from dotenv import load_dotenv

load_dotenv()

def init_db():
    schema_path = os.path.join(os.getcwd(), "schema.sql")
    if not os.path.exists(schema_path):
        print("❌ schema.sql not found")
        return

    print("📖 Reading schema.sql...")
    with open(schema_path, "r") as f:
        sql = f.read()

    # Split by semicolon to execute separate statements if needed, 
    # but SQLAlchemy text() can often handle multiple if the driver allows.
    # Postgres usually handles it fine.
    
    db = SessionLocal()
    try:
        print("🚀 Applying schema to database...")
        # We need to execute the SQL. 
        # Note: SQLAlchemy's execute(text(...)) might struggle with some multi-statement blobs depending on the driver.
        # But we'll try the direct approach first.
        
        # Filter out comments and empty lines to be safe
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt in statements:
            if stmt:
                db.execute(text(stmt))
        
        db.commit()
        print("✅ Schema applied successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error applying schema: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
