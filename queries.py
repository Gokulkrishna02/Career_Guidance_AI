from sqlalchemy import text

# =====================================================
# AUTH / USERS
# =====================================================

def create_user(db, name, gender, dob, email, password_hash):
    query = text("""
        INSERT INTO users (name, gender, date_of_birth, email, password_hash)
        VALUES (:name, :gender, :dob, :email, :password_hash)
        RETURNING user_id
    """)
    return db.execute(query, {
        "name": name,
        "gender": gender,
        "dob": dob,
        "email": email,
        "password_hash": password_hash
    }).fetchone()[0]


def get_user_by_email(db, email):
    query = text("""
        SELECT user_id, password_hash
        FROM users
        WHERE email = :email
    """)
    return db.execute(query, {"email": email}).fetchone()


def get_user_name(db, user_id):
    query = text("SELECT name FROM users WHERE user_id = :user_id")
    result = db.execute(query, {"user_id": user_id}).fetchone()
    return result[0] if result else "Student"


# =====================================================
# STUDENT PROFILE
# =====================================================

def create_student_profile(db, user_id, profile):
    query = text("""
        INSERT INTO student_profiles
        (user_id, education_level, class_or_degree, stream,
         marks, category, interest_area, location_preference, career_goal, budget_lpa)
        VALUES
        (:user_id, :education_level, :class_or_degree, :stream,
         :marks, :category, :interest_area, :location_preference, :career_goal, :budget_lpa)
        ON CONFLICT (user_id) DO UPDATE SET
            education_level = EXCLUDED.education_level,
            class_or_degree = EXCLUDED.class_or_degree,
            stream = EXCLUDED.stream,
            marks = EXCLUDED.marks,
            category = EXCLUDED.category,
            interest_area = EXCLUDED.interest_area,
            location_preference = EXCLUDED.location_preference,
            career_goal = EXCLUDED.career_goal,
            budget_lpa = EXCLUDED.budget_lpa,
            updated_at = CURRENT_TIMESTAMP
    """)
    db.execute(query, {
        "user_id": user_id,
        "education_level": profile.get("education_level"),
        "class_or_degree": profile.get("class_or_degree"),
        "stream": profile.get("stream"),
        "marks": profile.get("marks"),
        "category": profile.get("category"),
        "interest_area": profile.get("interest_area"),
        "location_preference": profile.get("location_preference"),
        "career_goal": profile.get("career_goal"),
        "budget_lpa": profile.get("budget_lpa"),
    })


def get_profile_by_user_id(db, user_id):
    query = text("""
        SELECT
            education_level,
            class_or_degree,
            stream,
            marks,
            category,
            interest_area,
            location_preference,
            career_goal,
            budget_lpa
        FROM student_profiles
        WHERE user_id = :user_id
    """)
    row = db.execute(query, {"user_id": user_id}).fetchone()

    if not row:
        return None

    return {
        "education_level": row[0],
        "class_or_degree": row[1],
        "stream": row[2],
        "marks": float(row[3]) if row[3] else 0.0,
        "category": row[4],
        "interest_area": row[5],
        "location_preference": row[6],
        "career_goal": row[7],
        "budget_lpa": float(row[8]) if row[8] else None,
    }


def update_student_profile(db, user_id, profile):
    query = text("""
        UPDATE student_profiles
        SET
            education_level = :education_level,
            class_or_degree = :class_or_degree,
            stream = :stream,
            marks = :marks,
            category = :category,
            interest_area = :interest_area,
            location_preference = :location_preference,
            career_goal = :career_goal,
            budget_lpa = :budget_lpa,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = :user_id
    """)
    db.execute(query, {
        "user_id": user_id,
        "education_level": profile.get("education_level"),
        "class_or_degree": profile.get("class_or_degree"),
        "stream": profile.get("stream"),
        "marks": profile.get("marks"),
        "category": profile.get("category"),
        "interest_area": profile.get("interest_area"),
        "location_preference": profile.get("location_preference"),
        "career_goal": profile.get("career_goal"),
        "budget_lpa": profile.get("budget_lpa"),
    })


# =====================================================
# COURSES / COLLEGES / RECOMMENDATION
# =====================================================

def get_course_id_by_name(db, course_name):
    query = text("""
        SELECT course_id
        FROM courses
        WHERE LOWER(course_name) = LOWER(:course_name)
    """)
    result = db.execute(query, {"course_name": course_name}).fetchone()
    return result[0] if result else None


def get_personalized_colleges(db, marks, category, course_id, year):
    query = text("""
        SELECT
            c.college_name,
            cu.cutoff_mark,
            p.avg_package_lpa,
            p.placement_percentage
        FROM cutoffs cu
        JOIN placements p
            ON cu.college_id = p.college_id
           AND cu.course_id = p.course_id
        JOIN colleges c ON c.college_id = cu.college_id
        WHERE cu.course_id = :course_id
          AND cu.year = :year
          AND cu.category = :category
          AND cu.cutoff_mark <= :marks
        ORDER BY
            p.avg_package_lpa DESC,
            cu.cutoff_mark DESC
    """)
    return db.execute(query, {
        "marks": marks,
        "category": category,
        "course_id": course_id,
        "year": year
    }).fetchall()


def get_eligible_colleges(db, marks, course_name, year, category):
    query = text("""
        SELECT c.college_name, cu.cutoff_mark
        FROM cutoffs cu
        JOIN colleges c ON cu.college_id = c.college_id
        JOIN courses cr ON cu.course_id = cr.course_id
        WHERE cr.course_name = :course_name
          AND cu.year = :year
          AND cu.category = :category
          AND cu.cutoff_mark <= :marks
        ORDER BY cu.cutoff_mark DESC
    """)
    return db.execute(query, {
        "course_name": course_name,
        "year": year,
        "category": category,
        "marks": marks
    }).fetchall()


def get_carriers_after_course(db, course_name):
    query = text("""
        SELECT ca.career_name, ca.avg_salary_lpa
        FROM course_careers cc
        JOIN careers ca ON cc.career_id = ca.career_id
        JOIN courses cr ON cc.course_id = cr.course_id
        WHERE cr.course_name = :course_name
    """)
    return db.execute(query, {"course_name": course_name}).fetchall()


def get_skills_for_career(db, career_name):
    query = text("""
        SELECT s.skill_name, cs.importance_level
        FROM career_skills cs
        JOIN skills s ON cs.skill_id = s.skill_id
        JOIN careers c ON cs.career_id = c.career_id
        WHERE c.career_name = :career_name
        ORDER BY cs.importance_level DESC
    """)
    return db.execute(query, {"career_name": career_name}).fetchall()


# =====================================================
# CHAT SESSIONS (SIDEBAR)
# =====================================================

def create_chat_session(db, user_id):
    query = text("""
        INSERT INTO chat_sessions (user_id, title)
        VALUES (:user_id, 'New Chat')
        RETURNING session_id
    """)
    return db.execute(query, {"user_id": user_id}).fetchone()[0]


def get_chat_sessions(db, user_id):
    query = text("""
        SELECT session_id, title
        FROM chat_sessions
        WHERE user_id = :user_id
        ORDER BY created_at DESC
    """)
    rows = db.execute(query, {"user_id": user_id}).fetchall()
    return [{"session_id": row[0], "title": row[1]} for row in rows]


def get_user_id_by_session(db, session_id):
    query = text("""
        SELECT user_id
        FROM chat_sessions
        WHERE session_id = :session_id
    """)
    result = db.execute(query, {"session_id": session_id}).fetchone()
    return result[0] if result else None


# =====================================================
# CHAT MESSAGES
# =====================================================

def get_chat_messages_by_session(db, session_id):
    query = text("""
        SELECT role, message, created_at
        FROM chat_messages
        WHERE session_id = :session_id
        ORDER BY created_at
    """)
    rows = db.execute(query, {"session_id": session_id}).fetchall()
    return [{"role": row[0], "message": row[1]} for row in rows]


def get_recent_chats(db, session_id, limit=5):
    query = text("""
        SELECT role, message
        FROM chat_messages
        WHERE session_id = :session_id
        ORDER BY created_at DESC
        LIMIT :limit
    """)
    return db.execute(query, {"session_id": session_id, "limit": limit}).fetchall()


def save_chat(db, session_id, role, message):
    query = text("""
        INSERT INTO chat_messages (session_id, role, message)
        VALUES (:session_id, :role, :message)
    """)
    db.execute(query, {"session_id": session_id, "role": role, "message": message})


# =====================================================
# SKILLS / GAP ANALYSIS
# =====================================================

def get_student_skills(db: Session, user_id: int):
    query = text("""
        SELECT s.skill_id, s.skill_name
        FROM student_skills ss
        JOIN skills s ON ss.skill_id = s.skill_id
        WHERE ss.user_id = :user_id
    """)
    return db.execute(query, {"user_id": user_id}).fetchall()


def insert_scraped_career(db: Session, data: dict):
    """Inserts a new career and its skills into the database."""
    import traceback
    try:
        # Check if career exists
        career_name = data["career_name"]
        existing = db.execute(
            text("SELECT career_id FROM careers WHERE career_name = :n"),
            {"n": career_name}
        ).fetchone()
        
        if existing:
            return existing[0]

        # Insert career
        print(f"DEBUG: Inserting career '{career_name}'")
        
        # Check if engine is SQLite to handle RETURNING compatibility
        engine_name = db.get_bind().name
        
        if engine_name == 'sqlite':
            db.execute(
                text("""
                    INSERT INTO careers (career_name, career_description, avg_salary_lpa, demand_score, growth_score)
                    VALUES (:n, :d, :s, :ds, :gs)
                """),
                {
                    "n": career_name,
                    "d": data["description"],
                    "s": data["avg_salary"],
                    "ds": data.get("demand_score", 70),
                    "gs": data.get("growth_score", 70)
                }
            )
            career_id = db.execute(text("SELECT last_insert_rowid()")).scalar()
        else:
            res = db.execute(
                text("""
                    INSERT INTO careers (career_name, career_description, avg_salary_lpa, demand_score, growth_score)
                    VALUES (:n, :d, :s, :ds, :gs) RETURNING career_id
                """),
                {
                    "n": career_name,
                    "d": data["description"],
                    "s": data["avg_salary"],
                    "ds": data.get("demand_score", 70),
                    "gs": data.get("growth_score", 70)
                }
            )
            career_id = res.fetchone()[0]
        
        print(f"DEBUG: Inserted career_id: {career_id}")

        # Insert skills and link them
        for skill in data["skills"]:
            sname = skill["name"]
            # Ensure skill exists in global skills table
            db.execute(
                text("INSERT INTO skills (skill_name) VALUES (:n) ON CONFLICT (skill_name) DO NOTHING"),
                {"n": sname}
            )
            sid_row = db.execute(
                text("SELECT skill_id FROM skills WHERE skill_name = :n"),
                {"n": sname}
            ).fetchone()
            
            if sid_row:
                sid = sid_row[0]
                # Link career to skill
                db.execute(
                    text("""
                        INSERT INTO career_skills (career_id, skill_id, importance_level)
                        VALUES (:cid, :sid, :il) ON CONFLICT DO NOTHING
                    """),
                    {"cid": career_id, "sid": sid, "il": skill.get("importance", 1)}
                )
        
        db.commit()
        return career_id
    except Exception as e:
        db.rollback()
        print(f"Error inserting scraped career: {e}")
        traceback.print_exc()
        return None


def get_student_skill_names(db, user_id) -> list:
    query = text("""
        SELECT s.skill_name
        FROM student_skills ss
        JOIN skills s ON ss.skill_id = s.skill_id
        WHERE ss.user_id = :user_id
    """)
    return [row[0] for row in db.execute(query, {"user_id": user_id}).fetchall()]


def add_student_skill(db, user_id, skill_id):
    query = text("""
        INSERT INTO student_skills (user_id, skill_id)
        VALUES (:user_id, :skill_id)
        ON CONFLICT DO NOTHING
    """)
    db.execute(query, {"user_id": user_id, "skill_id": skill_id})


def remove_student_skill(db, user_id, skill_id):
    query = text("""
        DELETE FROM student_skills
        WHERE user_id = :user_id AND skill_id = :skill_id
    """)
    db.execute(query, {"user_id": user_id, "skill_id": skill_id})


def get_skill_gap(db, user_id, career_name):
    query_req = text("""
        SELECT s.skill_name, cs.importance_level
        FROM career_skills cs
        JOIN skills s ON cs.skill_id = s.skill_id
        JOIN careers c ON cs.career_id = c.career_id
        WHERE c.career_name = :career_name
    """)
    required_skills = db.execute(query_req, {"career_name": career_name}).fetchall()

    user_skills = {row for row in get_student_skill_names(db, user_id)}

    gap = []
    for skill, importance in required_skills:
        if skill not in user_skills:
            gap.append({"skill": skill, "importance": importance})

    return sorted(gap, key=lambda x: x["importance"], reverse=True)


def get_skill_id_by_name(db, skill_name):
    query = text("SELECT skill_id FROM skills WHERE skill_name = :name")
    result = db.execute(query, {"name": skill_name}).fetchone()
    return result[0] if result else None


def create_skill(db, skill_name):
    query = text("INSERT INTO skills (skill_name) VALUES (:name) RETURNING skill_id")
    return db.execute(query, {"name": skill_name}).fetchone()[0]


def get_ranked_careers(db, user_id):
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        return []

    interest = profile["interest_area"].lower()

    query = text("""
        SELECT
            career_name,
            demand_score,
            growth_score
        FROM careers
        ORDER BY (demand_score + growth_score +
            CASE WHEN LOWER(career_name) LIKE :interest THEN 30 ELSE 0 END) DESC
        LIMIT 5
    """)

    rows = db.execute(query, {"interest": f"%{interest}%"}).fetchall()
    return [
        {
            "name": row[0],
            "score": row[1] + row[2],
            "demand": row[1],
            "growth": row[2]
        } for row in rows
    ]


# =====================================================
# FEEDBACK
# =====================================================

def save_feedback(db, user_id, session_id, rating, comment):
    query = text("""
        INSERT INTO ai_feedback (user_id, session_id, rating, comment)
        VALUES (:user_id, :session_id, :rating, :comment)
        RETURNING feedback_id
    """)
    return db.execute(query, {
        "user_id": user_id,
        "session_id": session_id,
        "rating": rating,
        "comment": comment
    }).fetchone()[0]


def get_avg_feedback_rating(db, user_id):
    query = text("""
        SELECT ROUND(AVG(rating)::numeric, 2)
        FROM ai_feedback
        WHERE user_id = :user_id
    """)
    result = db.execute(query, {"user_id": user_id}).fetchone()
    return float(result[0]) if result and result[0] else None


# =====================================================
# SKILL PROGRESS
# =====================================================

def upsert_skill_progress(db, user_id, skill_id, proficiency_level):
    query = text("""
        INSERT INTO skill_progress (user_id, skill_id, proficiency_level)
        VALUES (:user_id, :skill_id, :proficiency_level)
        ON CONFLICT (user_id, skill_id)
        DO UPDATE SET proficiency_level = EXCLUDED.proficiency_level,
                      updated_at = CURRENT_TIMESTAMP
    """)
    db.execute(query, {
        "user_id": user_id,
        "skill_id": skill_id,
        "proficiency_level": proficiency_level
    })


def get_skill_progress(db, user_id):
    query = text("""
        SELECT s.skill_name, sp.proficiency_level, sp.updated_at
        FROM skill_progress sp
        JOIN skills s ON sp.skill_id = s.skill_id
        WHERE sp.user_id = :user_id
        ORDER BY sp.updated_at DESC
    """)
    rows = db.execute(query, {"user_id": user_id}).fetchall()
    return [
        {
            "skill": row[0],
            "proficiency_level": row[1],
            "label": ["Beginner", "Elementary", "Intermediate", "Advanced", "Expert"][row[1] - 1],
            "updated_at": str(row[2])
        }
        for row in rows
    ]
