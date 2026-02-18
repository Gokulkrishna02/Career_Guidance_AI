from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from database import SessionLocal
from queries import *
from auth_utils import hash_password, verify_password
from rag.rag_index import  build_and_save_index, cached_rag_search
from datetime import datetime
import ollama

# ---------------- APP ----------------
RAG_CACHE = {}

app = FastAPI(title="Career Guidance AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------

class RegisterRequest(BaseModel):
    name: str
    gender: str | None = None
    date_of_birth: str | None = None
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
            dob = datetime.strptime(data.date_of_birth, "%d-%m-%Y").date()

        password_hash = hash_password(data.password)

        user_id = create_user(
            db=db,
            name=data.name,
            gender=data.gender,
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

        return {
            "message": "Login successful",
            "user_id": user_id
        }
    finally:
        db.close()

# ---------------- PROFILE ----------------

@app.post("/profile/setup/{user_id}")
def setup_profile(user_id: int, profile: ProfileSetupRequest):
    db = SessionLocal()
    try:
        create_student_profile(db, user_id, profile.dict())
        db.commit()

        # IMPORTANT: update RAG
        build_and_save_index()

        return {"message": "Profile setup completed"}
    finally:
        db.close()

@app.get("/profile/{user_id}")
def get_profile(user_id: int):
    db = SessionLocal()
    try:
        profile = get_profile_by_user_id(db, user_id)
        if not profile:
            return {"error": "Profile not found"}
        return profile
    finally:
        db.close()

@app.put("/profile/{user_id}")
def update_profile(user_id: int, profile: ProfileSetupRequest):
    db = SessionLocal()
    try:
        update_student_profile(db, user_id, profile.dict())
        db.commit()

        build_and_save_index()
        return {"message": "Profile updated successfully"}
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

        course_id = get_course_id_by_name(db, interest_area)
        if not course_id:
            return {"error": "Course not found"}

        colleges = get_personalized_colleges(
            db=db,
            marks=marks,
            category=category,
            course_id=course_id,
            year=year
        )

        return {
            "user_id": user_id,
            "interest": interest_area,
            "marks": marks,
            "recommendations": [
                {
                    "college": row[0],
                    "cutoff": row[1],
                    "avg_package_lpa": row[2],
                    "placement_percentage": row[3]
                }
                for row in colleges
            ]
        }
    finally:
        db.close()


# ---------------- AI GUIDANCE ----------------

def build_rag_context(profile, recommendations):
    marks, category, interest = profile

    student_context = f"""
Marks: {marks}
Category: {category}
Interested Course: {interest}
"""

    rec_text = ""
    for r in recommendations:
        rec_text += f"""
College: {r[0]}
Cutoff: {r[1]}
Average Package: {r[2]} LPA
Placement Percentage: {r[3]}%
"""

    return student_context, rec_text

async def generate_guidance_with_rag(student_context, recommendation_data):
    retrieved_docs = cached_rag_search(student_context + recommendation_data)

    prompt = f"""
You are an educational career guidance assistant.
Use ONLY the information provided.

Retrieved Knowledge:
{retrieved_docs}

Student Context:
{student_context}

College Recommendation:
{recommendation_data}

Tasks:
1. Explain why this college suits the student
2. Explain admission strategy
3. Suggest skills to start learning
4. Give next 6-month roadmap
"""

    response = await run_in_threadpool(
        ollama.chat,
        model="llama3.2:1b",
        messages=[{"role": "user", "content":prompt}],
        options={"temperature":0.3, "num_predict": 150}
    )

    return response["message"]["content"]

@app.get("/ai-guidance/{user_id}")
def ai_guidance(user_id: int, year: int = 2024):
    db = SessionLocal()
    try:
        # 1. Fetch profile
        profile = get_profile_by_user_id(db, user_id)
        if not profile:
            return {"error": "Profile not found"}

        marks = profile["marks"]
        category = profile["category"]
        interest = profile["interest_area"]

        # 2. Convert course name → course_id
        course_id = get_course_id_by_name(db, interest)
        if not course_id:
            return {"error": "Course not found"}

        # 3. Get personalized colleges
        recommendations = get_personalized_colleges(
            db=db,
            marks=marks,
            category=category,
            course_id=course_id,
            year=year
        )

        if not recommendations:
            return {"error": "No recommendations available"}

        # 4. Build RAG context
        student_context = f"""
Marks: {marks}
Category: {category}
Interested Course: {interest}
"""

        recommendation_data = ""
        for r in recommendations:
            recommendation_data += f"""
College: {r[0]}
Cutoff: {r[1]}
Average Package: {r[2]} LPA
Placement Percentage: {r[3]}%
"""

        # 5. Generate AI guidance
        ai_response = generate_guidance_with_rag(
            student_context=student_context,
            recommendation_data=recommendation_data
        )

        return {
            "user_id": user_id,
            "ai_guidance": ai_response
        }

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
        sessions = get_chat_sessions(db, user_id)
        return sessions   # ✅ already list[dict]
    finally:
        db.close()

@app.get("/chat/messages/{session_id}")
def get_chat_messages(session_id: int):
    db = SessionLocal()
    try:
        return get_chat_messages_by_session(db, session_id)
    finally:
        db.close()

def build_chat_prompt(student_context, retrieved_docs, chat_history, user_message):
    history_text = ""
    for role, msg in reversed(chat_history):
        history_text += f"{role.upper()}: {msg}\n"

    return f"""
You are a professional educational career counselor.

Use ONLY the information provided.
Do NOT hallucinate.

Student Profile:
{student_context}

Retrieved Knowledge:
{retrieved_docs}

Conversation So Far:
{history_text}

Student Question:
{user_message}

Respond clearly, practically, and motivationally.
"""



@app.post("/chat/{session_id}")
async def chat_with_ai(session_id: int, message: str):
    db = SessionLocal()
    try:
        # 1. Get session → user
        user_id = get_user_id_by_session(db, session_id)
        if user_id is None:
            return {"error": "Session not found. Please start a new chat."}

        # 2. Fetch profile
        profile = get_profile_by_user_id(db, user_id)
        if not profile:
            return {"error": "Profile not found"}

        # 3. Build student context (✅ FIX HERE)
        student_context = f"""
Marks: {profile["marks"]}
Category: {profile["category"]}
Interest: {profile["interest_area"]}
"""

        # 4. RAG retrieval
        retrieved_docs = cached_rag_search(message)

        # 5. Build prompt
        prompt = build_chat_prompt(
            student_context=student_context,
            retrieved_docs=retrieved_docs,
            chat_history=get_recent_chats(db, session_id),
            user_message=message
        )

        # 6. LLM call
        response = await run_in_threadpool(
            ollama.chat,
            model = "llama3.2:1b",
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature":0.3,
                "num_predict": 512
            }
        )

        ai_reply = response["message"]["content"]

        # 7. Save chat
        save_chat(db, session_id, "user", message)
        save_chat(db, session_id, "assistant", ai_reply)
        db.commit()

        return {"reply": ai_reply}

    finally:
        db.close()

