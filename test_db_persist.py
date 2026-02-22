from database import SessionLocal
from queries import insert_scraped_career
from scraper.collector import CareerScraper

def test_persistence():
    db = SessionLocal()
    scraper = CareerScraper()
    query = "Bio-Robotics Surgeon"
    print(f"Testing persistence for: {query}")
    data = scraper.search_career_info(query)
    print(f"Scraper data: {data}")
    
    cid = insert_scraped_career(db, data)
    print(f"Inserted Career ID: {cid}")
    
    # Verify
    from sqlalchemy import text
    if cid:
        res = db.execute(text("SELECT career_name, avg_salary_lpa FROM careers WHERE career_id = :cid"), {"cid": cid}).fetchone()
        print(f"Verified from DB: {res}")
    else:
        print("ERROR: cid is None, insertion failed.")
    db.close()

if __name__ == "__main__":
    test_persistence()
