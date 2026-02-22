import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
try:
    from database import SessionLocal
except Exception:
    SessionLocal = None

from rag_documents import get_all_documents

def build_documents_from_db():
    """Build RAG documents from DB (college/placement data) + rich static knowledge."""
    documents = list(get_all_documents())  # Always include static knowledge

    try:
        db = SessionLocal()
        query = text("""
            SELECT
                c.college_name,
                cr.course_name,
                p.avg_package_lpa,
                p.placement_percentage
            FROM placements p
            JOIN colleges c ON p.college_id = c.college_id
            JOIN courses cr ON p.course_id = cr.course_id
        """)
        rows = db.execute(query).fetchall()
        db.close()

        for college, course, avg_pkg, placement in rows:
            doc = (
                f"College: {college} | Course: {course} | "
                f"Average Package: {avg_pkg} LPA | Placement: {placement}%. "
                f"This college offers strong opportunities for {course} graduates."
            )
            documents.append(doc)
    except Exception as e:
        # DB unavailable — static docs are sufficient fallback
        pass

    return documents
