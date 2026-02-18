from sqlalchemy import text
from database import SessionLocal

def build_documents_from_db():
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

    documents = []
    for college, course, avg_pkg, placement in rows:
        doc = f"""
College: {college}
Course: {course}
Average Package: {avg_pkg} LPA
Placement Percentage: {placement}%

This college provides good academic and placement support for students interested in {course}.
"""
        documents.append(doc.strip())

    return documents
