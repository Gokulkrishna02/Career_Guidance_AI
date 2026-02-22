from database import SessionLocal
from queries import insert_scraped_career
from scraper.collector import CareerScraper

def test_persistence():
    db = SessionLocal()
    scraper = CareerScraper()
    query = "Quantum Computing Researcher"
    print(f"Testing persistence for: {query}")
    data = scraper.search_career_info(query)
    print(f"Scraper data: {data}")
    
    cid = insert_scraped_career(db, data)
    print(f"Inserted Career ID: {cid}")
    
    # Verify
    from sqlalchemy import text
    res = db.execute(text("SELECT career_name FROM careers WHERE career_id = :cid"), {"cid": cid}).fetchone()
    print(f"Verified from DB: {res}")
    db.close()

if __name__ == "__main__":
    test_persistence()
