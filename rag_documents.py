"""
Expanded RAG Knowledge Base for Career Guidance AI
Contains static, high-quality career and education documents that are always loaded
into the FAISS index regardless of DB connectivity.
"""

STATIC_DOCUMENTS = [
    # ── Software / CS Careers ──────────────────────────────────────────────────
    "A Software Engineer designs, develops, and maintains software applications. "
    "To enter this field, students should master Data Structures, Algorithms, and at least one language (Python, Java, or C++). "
    "Key platforms to practice: LeetCode, HackerRank. Average fresher package in India: 6-15 LPA.",

    "Data Scientists work with large datasets to find patterns and build predictive models. "
    "Required skills: Python, NumPy, Pandas, Scikit-learn, SQL, and visualization tools like Matplotlib or Tableau. "
    "Top hiring companies: Google, Amazon, Flipkart, Razorpay. Avg salary: 10-20 LPA.",

    "AI/ML Engineers develop artificial intelligence models including deep learning, NLP, and computer vision systems. "
    "Core technologies: TensorFlow, PyTorch, Transformers (HuggingFace), CUDA. "
    "This is one of the fastest-growing fields globally. Expected growth: 40% in the next decade. Avg salary: 15-30 LPA.",

    "Cybersecurity Analysts protect computer systems from threats, breaches, and hackers. "
    "Key skills: Ethical Hacking, Networking (TCP/IP), Linux, Firewalls, SIEM tools. "
    "Certifications: CEH, OSCP, CompTIA Security+. Avg salary: 8-14 LPA in India.",

    "Cloud Engineers design and manage cloud infrastructure using AWS, Azure, or GCP. "
    "Skills needed: Linux, Docker, Kubernetes, Terraform, CI/CD pipelines. "
    "Cloud is the backbone of modern tech. Avg salary: 10-18 LPA. Huge demand globally.",

    # ── Engineering Careers ────────────────────────────────────────────────────
    "Mechanical Engineers design and analyze machines, systems, and manufacturing processes. "
    "Core subjects: Thermodynamics, Fluid Mechanics, Machine Design, CAD/CAM. "
    "Career paths: Automobile, Aerospace, Manufacturing, HVAC. Avg salary: 4-9 LPA.",

    "Civil Engineers plan and construct buildings, bridges, roads and infrastructure. "
    "Core subjects: Structural Analysis, Surveying, Concrete Technology, AutoCAD. "
    "Government jobs (PWD, NHAI, TNPSC) are popular in India. Avg salary: 4-8 LPA.",

    "Electrical and Electronics Engineers (EEE) work in power systems, embedded systems, and VLSI. "
    "Key skills: MATLAB, PLC, Circuit Design, Power Electronics. "
    "Growing opportunities in EV sector and renewable energy. Avg salary: 5-10 LPA.",

    # ── Medical / Healthcare ───────────────────────────────────────────────────
    "Doctors (MBBS) must clear NEET UG with high scores (General: 600+/720) to get into good colleges. "
    "After MBBS, specialization (MD/MS) is required for higher paying roles. "
    "Areas: Surgery, Dermatology, Cardiology. Avg salary: 8-20 LPA depending on specialization.",

    "Nursing is a growing healthcare profession with global demand, especially in the US, UK, Canada, and Gulf countries. "
    "Required: GNM or B.Sc Nursing. IELTS/NCLEX required for abroad. Avg salary in India: 3-6 LPA.",

    # ── Commerce / Finance ─────────────────────────────────────────────────────
    "Chartered Accountants (CA) are in high demand in India for audit, taxation, and financial consulting. "
    "Path: CA Foundation → Intermediate → Final + Articleship. 3 level exams conducted by ICAI. "
    "Avg salary after qualification: 8-15 LPA. Top recruiters: Big 4 firms (Deloitte, EY, PwC, KPMG).",

    "Investment Bankers work in mergers, acquisitions, and capital markets. "
    "Entry via MBA (Finance) from IIMs, ISB. Skills: Financial Modeling, Excel, Valuation. "
    "Avg fresher salary: 12-25 LPA at top investment banks.",

    # ── Design / Creative ──────────────────────────────────────────────────────
    "UX/UI Designers create user-friendly digital interfaces for apps and websites. "
    "Key tools: Figma, Adobe XD, Sketch. Core skills: User Research, Wireframing, Accessibility. "
    "Avg salary: 6-12 LPA. High demand in product-based companies and startups.",

    # ── Entrance Examinations ─────────────────────────────────────────────────
    "JEE Main and Advanced are gateway exams for IITs, NITs, and IIITs. "
    "JEE Main: 90 days preparation with focus on Physics, Chemistry, Maths. "
    "Recommended books: HC Verma (Physics), OP Tandon (Chemistry), SL Loney (Maths).",

    "NEET UG is the national entrance test for MBBS and BDS admissions in India. "
    "Syllabus: Class 11 and 12 Biology, Physics, Chemistry. "
    "Total marks: 720. Cutoff for Government MBBS (General): typically 550+.",

    "TNEA (Tamil Nadu Engineering Admissions) is a counselling-based process. "
    "No entrance exam; admission based on 12th marks. Cutoff varies by college and stream. "
    "Higher cutoffs: CSE > IT > ECE > Mechanical > EEE > Civil.",

    "CLAT (Common Law Admission Test) is for National Law University (NLU) admissions. "
    "Sections: English, GK, Legal Reasoning, Maths, Logical Reasoning. "
    "Best NLUs: NLSIU Bangalore, NLU Delhi, NALSAR Hyderabad.",

    # ── Study Roadmaps ─────────────────────────────────────────────────────────
    "6-Month Roadmap for CSE Freshers: Month 1-2: Learn Python and core data structures. "
    "Month 3: Practice 100+ LeetCode problems (Easy/Medium). "
    "Month 4: Learn DSA deeply (Trees, Graphs, DP). "
    "Month 5: Build 2-3 projects (web app, ML model, or API). "
    "Month 6: Apply for internships, prepare resume, attend mock interviews.",

    "Skill Development Path for Data Science: "
    "Step 1: Python basics (3 weeks). Step 2: Statistics and Probability (2 weeks). "
    "Step 3: Pandas, NumPy, Matplotlib (3 weeks). Step 4: Machine Learning with Scikit-learn (4 weeks). "
    "Step 5: Deep Learning basics (TensorFlow/PyTorch) (4 weeks). Step 6: Kaggle competitions.",

    "For Commerce students aiming at MBA: "
    "Prepare for CAT, XAT, or MAT from 3rd year of graduation. "
    "Focus: Quantitative Aptitude, Verbal Ability, Data Interpretation. "
    "Top colleges: IIM A/B/C, XLRI, FMS Delhi. CAT cutoff for IIM-A: 99+ percentile.",

    # ── High-Ranking Indian Colleges ──────────────────────────────────────────
    "IIT Madras offers world-class education in engineering, sciences, and management. "
    "It consistently ranks #1 in NIRF. Average CSE package: 25-35 LPA. Top recruiters: Google, Microsoft, Goldman Sachs.",

    "NIT Trichy (National Institute of Technology, Tiruchirappalli) is one of the top NITs. "
    "Average CSE package: 15-20 LPA. Strong alumni network and research culture.",

    "VIT Vellore (Vellore Institute of Technology) accepts students through VITEEE. "
    "Known for excellent placements and modern infrastructure. Average package: 8-12 LPA.",

    "Anna University is the affiliating university for most engineering colleges in Tamil Nadu. "
    "Top affiliated colleges: CEG (Chennai), Thiagarajar College of Engineering (Madurai).",

    "PSG College of Technology, Coimbatore is a top institution for engineering in Tamil Nadu. "
    "Known for strong industry connections and hands-on learning. Average package: 7-12 LPA.",

    # ── Scholarships ──────────────────────────────────────────────────────────
    "SC/ST students can apply for National Fellowship by UGC for higher education funding. "
    "OBC students: Non-creamy layer certificate is required for reservations in central institutions. "
    "Merit-cum-Means scholarship from AICTE: Available for students with family income below 8 LPA.",

    "Post-Matric Scholarship by Tamil Nadu government supports SC/ST/OBC students for college education. "
    "Amount: Covers tuition fees and provides a monthly stipend.",

    # ── Soft Skills & Career Readiness ────────────────────────────────────────
    "Communication skills are vital for all careers. Practice public speaking, writing, and active listening. "
    "Courses: Coursera 'English for Career Development', Toastmasters clubs, LinkedIn Learning.",

    "Building a strong LinkedIn profile increases visibility to recruiters by 40x. "
    "Tips: Add profile photo, include all skills, write a strong summary, and post regularly.",

    "Resume tips for freshers: Keep it to 1 page. Include internships, projects, certifications, and skills. "
    "Avoid generic objectives. Use action verbs: 'Built', 'Designed', 'Analyzed', 'Led'.",
]


def get_all_documents():
    """Returns all static knowledge documents."""
    return STATIC_DOCUMENTS
