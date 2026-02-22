# Career Guidance AI — System Architecture & Flow

This document provides a comprehensive step-by-step explanation of how the Career Guidance AI functions, from the user's first login to the advanced "self-healing" knowledge discovery.

---

## 🚀 1. The User Journey (Step-by-Step)

### Step 1: Authentication (`auth_utils.py` + `login.html`)
- **Process**: User registers or logs in via a glassmorphism interface.
- **Logic**: `auth_utils.py` ensures passwords are never stored in plain text (using `bcrypt` with SHA-256 normalization). The backend (`main.py`) issues a user ID and checks if a profile already exists.

### Step 2: Dynamic Onboarding (`profile-setup.html`)
- **Process**: New users provide their education, interests, and target careers.
- **Logic**: Skills are captured as "pills". Upon saving, the backend (`main.py`) stores this in the database and triggers an initial RAG indexing specialized for that user's interests.

### Step 3: Central Dashboard (`index.html`)
- **Process**: The dashboard loads three core modules simultaneously:
  1. **Career Ranking**: Shows "Match Percentage" based on the student's profile.
  2. **Skill Progress**: Allows users to track their learning journey.
  3. **AI Chat**: A real-time interface for personalized guidance.

---

## 🧠 2. Deep-Dive: Core System Flows

### Flow A: The AI Recommendation Engine
1. **Request**: User asks for a "Career Roadmap".
2. **Scoring**: `ml/career_scorer.py` runs a weighted algorithm (Match = Marks + Interest + Skill Overlap).
3. **Retrieval (RAG)**: `rag/rag_index.py` searches the `FAISS` vector store for relevant documents in `rag_documents.py`.
4. **Generation**: The LLM (Llama 3.2:1b) combines your profile, your match scores, and the retrieved facts to produce a structured roadmap.

### Flow B: Self-Healing Knowledge Discovery (The "Web Discovery" Flow)
1. **Trigger**: User asks about a rare or new career (e.g., "Bio-Robotics Surgeon").
2. **Detection**: `main.py` detects that the career is not in the local Knowledge Base (`CAREER_KB`).
3. **Scraping**: `scraper/collector.py` is invoked to perform an "on-demand" discovery.
4. **Persistence**: The discovered data (description, average salary, required skills) is automatically saved to the database via `queries.py`.
5. **Update**: The AI now responds using this "freshly learned" information.

---

## 📂 3. File-by-File Responsibility

### Backend & Infrastructure
- **`main.py`**: The "Brain" of the system. Orchestrates API requests, AI chat logic, and coordinates between the database and ML engines.
- **`database.py`**: The "Resilience Layer". Automatically switches from Supabase (Cloud) to SQLite (Local) if the network is restricted.
- **`queries.py`**: The "Data Manager". Contains all SQL logic for saving users, profiles, feedback, and discovered careers.
- **`init_db.py`**: The "Initializer". Sets up the tables and schema required for the app to run.

### Intelligence Layer
- **`ml/career_scorer.py`**: Contains the hard logic for calculating match scores, demand scores, and growth outlooks for 12+ primary domains.
- **`rag/rag_index.py`**: Manages the Vector Search. It converts text documents into mathematical vectors to find "similar" information fast.
- **`rag_documents.py`**: The "Encyclopedia". A massive static dataset of exams, career paths, and 6-month roadmaps.

### Frontend
- **`frontend/css/style.css`**: Defines the "Rich Aesthetic" — glassmorphism, dark mode, and animations.
- **`frontend/index.html`**: The main user cockpit.
- **`frontend/login.html`**: Secure entry point.

---

## 🛡️ 4. Resilience & Security
- **Fault Tolerance**: If the AI model (Ollama) is offline, the system still provides rule-based recommendations from `career_scorer.py`.
- **Database Fallback**: The app starts even without a database connection, enabling offline exploration of the ML knowledge base.
