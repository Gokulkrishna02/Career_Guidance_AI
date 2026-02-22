from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal
from queries import *
from auth_utils import hash_password, verify_password
from rag.rag_index import build_and_save_index, cached_rag_search
from ml.career_scorer import score_careers
from datetime import datetime
import ollama

# ---------------- APP ----------------
app = FastAPI(title="Career Guidance AI Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------

class RegisterRequest(BaseModel):
    name: str
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ProfileSetupRequest(BaseModel):
    education_level: str
    class_or_degree: str
    stream: str
    marks: float
    category: str
    interest_area: str
    location_preference: str
    career_goal: str
    budget_lpa: Optional[float] = None
    skills: Optional[str] = None  # Comma-separated

class FeedbackRequest(BaseModel):
    user_id: int
    session_id: Optional[int] = None
    rating: int  # 1-5
    comment: Optional[str] = ""

class SkillProgressRequest(BaseModel):
    skill_name: str
    proficiency_level: int  # 1-5

class AddSkillRequest(BaseModel):
    skill_name: str

# ---------------- ADMIN ----------------

@app.post("/admin/rebuild-vector-db")
def rebuild_vector_db():
    build_and_save_index()
    return {"message": "Vector database rebuilt successfully"}

# ---------------- AUTH ----------------

@app.post("/auth/register")
def register_user(data: RegisterRequest):
    db = SessionLocal()
    try:
        dob = None
        if data.date_of_birth:
            try:
                dob = datetime.strptime(data.date_of_birth, "%d-%m-%Y").date()
            except ValueError:
                return {"error": "Invalid date format. Use DD-MM-YYYY"}

        # Check duplicate email
        existing = get_user_by_email(db, data.email)
        if existing:
            return {"error": "An account with this email already exists"}

        password_hash = hash_password(data.password)
        user_id = create_user(
            db=db,
            name=data.name,
            gender=data.gender or "Not specified",
            dob=dob,
            email=data.email,
            password_hash=password_hash
        )
        db.commit()
        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "next": "profile-setup"
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Registration failed: {str(e)}"}
    finally:
        db.close()


@app.post("/auth/login")
def login_user(data: LoginRequest):
    db = SessionLocal()
    try:
        user = get_user_by_email(db, data.email)
        if not user:
            return {"error": "Invalid email or password"}

        user_id, password_hash = user
        if not verify_password(data.password, password_hash):
            return {"error": "Invalid email or password"}

        name = get_user_name(db, user_id)
        return {
            "message": "Login successful",
            "user_id": user_id,
            "name": name
        }
    finally:
        db.close()

# ---------------- PROFILE ----------------

@app.post("/profile/setup/{user_id}")
def setup_profile(user_id: int, profile: ProfileSetupRequest):
    db = SessionLocal()
    try:
        profile_data = profile.dict()
        skills_str = profile_data.pop("skills", "") or ""

        create_student_profile(db, user_id, profile_data)

        # Handle skills
        if skills_str:
            for s_name in [s.strip() for s in skills_str.split(",") if s.strip()]:
                skill_id = get_skill_id_by_name(db, s_name)
                if not skill_id:
                    skill_id = create_skill(db, s_name)
                add_student_skill(db, user_id, skill_id)

        db.commit()

        # Rebuild RAG index in background-safe way
        try:
            build_and_save_index()
        except Exception:
            pass  # Non-critical

        return {"message": "Profile setup completed"}
    except Exception as e:
        db.rollback()
        return {"error": f"Profile setup failed: {str(e)}"}
    finally:
        db.close()


@app.get("/profile/{user_id}")
def get_profile(user_id: int):
    db = SessionLocal()
    try:
        profile = get_profile_by_user_id(db, user_id)
        if not profile:
            return {"error": "Profile not found"}
        # Also attach skills
        skills = get_student_skill_names(db, user_id)
        profile["skills"] = skills
        name = get_user_name(db, user_id)
        profile["name"] = name
        return profile
    finally:
        db.close()


@app.put("/profile/{user_id}")
def update_profile(user_id: int, profile: ProfileSetupRequest):
    db = SessionLocal()
    try:
        profile_data = profile.dict()
        skills_str = profile_data.pop("skills", "") or ""

        update_student_profile(db, user_id, profile_data)

        # Re-sync skills: clear then re-add
        current_skills = get_student_skills(db, user_id)
        for skill_id, _ in current_skills:
            remove_student_skill(db, user_id, skill_id)

        if skills_str:
            for s_name in [s.strip() for s in skills_str.split(",") if s.strip()]:
                skill_id = get_skill_id_by_name(db, s_name)
                if not skill_id:
                    skill_id = create_skill(db, s_name)
                add_student_skill(db, user_id, skill_id)

        db.commit()
        try:
            build_and_save_index()
        except Exception:
            pass
        return {"message": "Profile updated successfully"}
    except Exception as e:
        db.rollback()
        return {"error": f"Update failed: {str(e)}"}
    finally:
        db.close()

# ---------------- SKILLS MANAGEMENT ----------------

@app.get("/skills/{user_id}")
def get_skills(user_id: int):
    db = SessionLocal()
    try:
        skills = get_student_skill_names(db, user_id)
        return {"skills": skills}
    finally:
        db.close()


@app.post("/skills/{user_id}")
def add_skill(user_id: int, data: AddSkillRequest):
    db = SessionLocal()
    try:
        skill_id = get_skill_id_by_name(db, data.skill_name)
        if not skill_id:
            skill_id = create_skill(db, data.skill_name)
        add_student_skill(db, user_id, skill_id)
        db.commit()
        return {"message": f"Skill '{data.skill_name}' added successfully"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

# ---------------- SKILL PROGRESS ----------------

@app.post("/skill-progress/{user_id}")
def update_skill_progress(user_id: int, data: SkillProgressRequest):
    db = SessionLocal()
    try:
        skill_id = get_skill_id_by_name(db, data.skill_name)
        if not skill_id:
            skill_id = create_skill(db, data.skill_name)
            add_student_skill(db, user_id, skill_id)
        upsert_skill_progress(db, user_id, skill_id, data.proficiency_level)
        db.commit()
        return {"message": f"Progress for '{data.skill_name}' updated to level {data.proficiency_level}"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


@app.get("/skill-progress/{user_id}")
def get_my_skill_progress(user_id: int):
    db = SessionLocal()
    try:
        progress = get_skill_progress(db, user_id)
        return {"skill_progress": progress}
    finally:
        db.close()

# ---------------- ML CAREER SCORING (NEW) ----------------

@app.get("/career-ranking/{user_id}")
def career_ranking(user_id: int):
    db = SessionLocal()
    try:
        profile = get_profile_by_user_id(db, user_id)
        if not profile:
            return {"error": "Profile not found. Please complete your profile first."}

        student_skills = get_student_skill_names(db, user_id)

        # Use the ML scorer (works offline, no DB needed for scoring)
        rankings = score_careers(
            interest_area=profile.get("interest_area", ""),
            career_goal=profile.get("career_goal", ""),
            stream=profile.get("stream", ""),
            marks=float(profile.get("marks", 0)),
            student_skills=student_skills,
        )

        # Also try to enhance with DB data
        try:
            db_rankings = get_ranked_careers(db, user_id)
            if db_rankings:
                # Merge DB rankings by boosting matching names
                db_names = {r["name"].lower(): r for r in db_rankings}
                for r in rankings:
                    if r["name"].lower() in db_names:
                        r["score"] = min(100, r["score"] + 5)
        except Exception:
            pass

        return {"rankings": rankings[:8]}  # Top 8
    finally:
        db.close()

# ---------------- SKILL GAP ----------------

@app.get("/skill-gap/{user_id}")
def skill_gap_analysis(user_id: int, career_name: Optional[str] = None):
    db = SessionLocal()
    try:
        profile = get_profile_by_user_id(db, user_id)

        if not career_name and profile:
            career_name = profile.get("career_goal") or profile.get("interest_area")

        if not career_name:
            return {"error": "Target career unknown. Please complete your profile."}

        student_skills = get_student_skill_names(db, user_id)

        # Try DB-based gap analysis first
        try:
            gap = get_skill_gap(db, user_id, career_name)
            if gap:
                return {"career": career_name, "missing_skills": gap, "source": "database"}
        except Exception:
            pass

        # Fallback: use ML knowledge base
        from ml.career_scorer import CAREER_KB
        target = career_name.lower()
        career_data = next(
            (c for c in CAREER_KB if target in c["name"].lower() or
             any(kw in target for kw in c["keywords"])),
            None
        )

        if career_data:
            student_lower = {s.lower() for s in student_skills}
            missing = [
                {"skill": rs, "importance": 3 - i if i < 3 else 1}
                for i, rs in enumerate(career_data["required_skills"])
                if rs.lower() not in student_lower
            ]
            return {"career": career_name, "missing_skills": missing, "source": "ai_knowledge"}

        return {"career": career_name, "missing_skills": [], "message": "No skill data available for this career."}
    finally:
        db.close()

# ---------------- RECOMMENDATION ----------------

@app.get("/personalized-recommendation/{user_id}")
def personalized_recommendation(user_id: int, year: int = 2024):
    db = SessionLocal()
    try:
        profile = get_profile_by_user_id(db, user_id)
        if not profile:
            return {"error": "Profile not found"}

        marks = profile["marks"]
        category = profile["category"]
        interest_area = profile["interest_area"]
        budget = profile.get("budget_lpa")

        course_id = get_course_id_by_name(db, interest_area)
        if not course_id:
            # Return message if no college data seeded yet
            return {
                "user_id": user_id,
                "interest": interest_area,
                "marks": marks,
                "recommendations": [],
                "note": "No college data for this interest area yet. Use the Career Chat for AI-powered guidance."
            }

        colleges = get_personalized_colleges(
            db=db, marks=marks, category=category, course_id=course_id, year=year
        )

        recs = []
        for row in colleges:
            status = "Within Budget"
            if budget and budget > 0:
                if row[2] < (budget / 4):
                    status = "High Value"
                elif row[2] > budget:
                    status = "Expensive"
            recs.append({
                "college": row[0],
                "cutoff": float(row[1]),
                "avg_package_lpa": float(row[2]),
                "placement_percentage": float(row[3]),
                "status": status
            })

        return {
            "user_id": user_id,
            "interest": interest_area,
            "marks": marks,
            "recommendations": recs
        }
    finally:
        db.close()

# ---------------- AI GUIDANCE ----------------

def build_rag_context(profile: dict, student_skills: list) -> str:
    return f"""
Student Profile:
- Education: {profile.get('education_level')} ({profile.get('class_or_degree')})
- Stream: {profile.get('stream')}
- Marks: {profile.get('marks')}%
- Category: {profile.get('category')}
- Interest Area: {profile.get('interest_area')}
- Career Goal: {profile.get('career_goal')}
- Location Preference: {profile.get('location_preference')}
- Current Skills: {', '.join(student_skills) if student_skills else 'Not specified'}
""".strip()


@app.get("/ai-guidance/{user_id}")
async def ai_guidance(user_id: int):
    db = SessionLocal()
    try:
        profile = get_profile_by_user_id(db, user_id)
        if not profile:
            return {"error": "Profile not found"}

        student_skills = get_student_skill_names(db, user_id)
        
        # --- DYNAMIC DISCOVERY ---
        target = profile.get("career_goal") or profile.get("interest_area", "Engineering")
        from scraper.collector import CareerScraper
        scraper = CareerScraper()
        discovery_data = scraper.search_career_info(target)
        
        if not discovery_data.get("found"):
            print(f"🌐 Discovered new career: {target}. Persisting to DB.")
            from queries import insert_scraped_career
            insert_scraped_career(db, discovery_data)
        # -------------------------

        student_context = build_rag_context(profile, student_skills)
        
        # ML career ranking for context
        top_careers = score_careers(
            interest_area=profile.get("interest_area", ""),
            career_goal=profile.get("career_goal", ""),
            stream=profile.get("stream", ""),
            marks=float(profile.get("marks", 0)),
            student_skills=student_skills,
        )[:3]

        career_context = "\n".join(
            f"- {c['name']} (Match: {c['score']}%, Avg Salary: {c['avg_salary_lpa']} LPA, "
            f"Missing Skills: {', '.join(c['missing_skills'][:3]) or 'None'})"
            for c in top_careers
        )

        retrieved_docs = cached_rag_search(student_context)
        rag_text = "\n---\n".join(retrieved_docs) if isinstance(retrieved_docs, list) else str(retrieved_docs)

        prompt = f"""
You are a professional educational career counselor AI. Provide personalized, actionable guidance.

Student Profile:
{student_context}

Top Career Matches (AI-Scored):
{career_context}

Retrieved Knowledge:
{rag_text}

Your Task:
1. Recommend the top 2 most suitable careers for this student with explanation
2. Suggest the most critical skills to learn (prioritize missing skills)
3. Provide a concrete 6-month action plan with weekly milestones
4. Mention any relevant entrance exams or certifications
5. Give one motivational insight tailored to this student

Be specific, honest, and encouraging. Do NOT hallucinate college names or salary figures.
"""

        response = await run_in_threadpool(
            ollama.chat,
            model="llama3.2:1b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.4, "num_predict": 400}
        )

        return {"user_id": user_id, "ai_guidance": response["message"]["content"]}
    finally:
        db.close()

# ---------------- CHAT (SESSION BASED) ----------------

@app.post("/chat/session/{user_id}")
def create_chat_session_api(user_id: int):
    db = SessionLocal()
    try:
        session_id = create_chat_session(db, user_id)
        db.commit()
        return {"session_id": session_id}
    finally:
        db.close()


@app.get("/chat/sessions/{user_id}")
def list_chat_sessions(user_id: int):
    db = SessionLocal()
    try:
        return get_chat_sessions(db, user_id)
    finally:
        db.close()


@app.get("/chat/messages/{session_id}")
def get_chat_messages(session_id: int):
    db = SessionLocal()
    try:
        return get_chat_messages_by_session(db, session_id)
    finally:
        db.close()


def build_chat_prompt(student_context: str, retrieved_docs, chat_history, user_message: str) -> str:
    history_text = ""
    for role, msg in reversed(chat_history):
        history_text += f"{role.upper()}: {msg}\n"

    rag_text = "\n---\n".join(retrieved_docs) if isinstance(retrieved_docs, list) else str(retrieved_docs)

    return f"""
You are a professional educational career counselor AI named CareerBot.
Use ONLY the information provided below. Do NOT hallucinate.
Be specific, practical, and encouraging.

Student Profile:
{student_context}

Retrieved Knowledge:
{rag_text}

Conversation History:
{history_text}

Student's Question:
{user_message}

Provide a clear, helpful, and motivating response. Reference the student's specific profile where relevant.
Respond in 3-5 sentences for casual questions, or in structured bullet-points for detailed guidance questions.
"""


@app.post("/chat/{session_id}")
async def chat_with_ai(session_id: int, message: str):
    db = SessionLocal()
    try:
        user_id = get_user_id_by_session(db, session_id)
        if user_id is None:
            return {"error": "Session not found. Please start a new chat."}

        # --- DYNAMIC DISCOVERY ---
        career_keywords = ["career", "become", "job", "salary", "skills for", "how to be a"]
        if any(k in message.lower() for k in career_keywords):
            from scraper.collector import CareerScraper
            scraper = CareerScraper()
            discovery = scraper.search_career_info(message)
            if not discovery.get("found") and len(message.split()) < 10:
                print(f"🌐 Dynamic discovery triggered in chat: {message}")
                from queries import insert_scraped_career
                insert_scraped_career(db, discovery)
        # -------------------------

        # 1. Fetch history for context
        history = get_chat_history(db, session_id, limit=5)
        
        # 2. Get user info for grounding
        user_id_row = db.execute(text("SELECT user_id FROM chat_sessions WHERE session_id = :s"), {"s": session_id}).fetchone()
        profile_json = "{}"
        if user_id_row:
            p = get_profile_by_user_id(db, user_id_row[0])
            if p:
                profile_json = json.dumps(p)

        # 3. RAG Search
        docs = cached_rag_search(message, top_k=3)
        context = "\n\n".join(docs)

        chat_messages = [{"role": m["role"], "content": m["message"]} for m in history]
        
        # System prompt with profile grounding
        system_msg = f"""
You are a helpful Career AI Counselor.
User Profile: {profile_json}
Context from Knowledge Base: {context}

Answer the user's career questions accurately based on the context and their profile.
If you don't know the answer, say you are searching for more details.
"""
        chat_messages.insert(0, {"role": "system", "content": system_msg})
        chat_messages.append({"role": "user", "content": message})

        response = await run_in_threadpool(
            ollama.chat,
            model="llama3.2:1b",
            messages=chat_messages,
        )
        
        reply = response["message"]["content"]
        save_chat_message(db, session_id, "user", message)
        save_chat_message(db, session_id, "assistant", reply)
        db.commit()

        return {"reply": reply}
    finally:
        db.close()

# ---------------- FEEDBACK ----------------

@app.post("/feedback")
def submit_feedback(data: FeedbackRequest):
    db = SessionLocal()
    try:
        if not (1 <= data.rating <= 5):
            return {"error": "Rating must be between 1 and 5"}
        fid = save_feedback(db, data.user_id, data.session_id, data.rating, data.comment)
        db.commit()
        return {"message": "Thank you for your feedback!", "feedback_id": fid}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


@app.get("/feedback/{user_id}")
def get_feedback_summary(user_id: int):
    db = SessionLocal()
    try:
        avg = get_avg_feedback_rating(db, user_id)
        return {"average_rating": avg, "message": "Your feedback helps us improve!"}
    finally:
        db.close()

# ---------------- WEB SEARCH (FALLBACK) ----------------

from scraper.collector import CareerScraper
scraper = CareerScraper()

@app.get("/web-search")
def web_search(query: str):
    info = scraper.search_career_info(query)
    return info
