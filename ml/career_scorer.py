"""
Career Scoring Engine
Implements a hybrid ML-inspired scoring algorithm based on:
  - Student marks, category, interest, skills, and career goal text similarity
  - Career demand, growth, and skill match ratios
This module runs purely on in-memory logic — no trained model file required.
"""

import re

# ─── Career knowledge base ────────────────────────────────────────────────────
# Each entry has: name, keywords (for interest matching), required_skills,
# demand_score (0-100), growth_score (0-100), avg_salary_lpa, streams

CAREER_KB = [
    {
        "name": "Software Engineer",
        "keywords": ["software", "programming", "coding", "computer", "cse", "it", "development"],
        "required_skills": ["Python", "Data Structures", "Algorithms", "Problem Solving", "Git"],
        "demand_score": 95,
        "growth_score": 88,
        "avg_salary_lpa": 12.0,
        "streams": ["CSE", "IT", "Computer Science"],
        "min_marks": 55.0,
    },
    {
        "name": "Data Scientist",
        "keywords": ["data", "machine learning", "ai", "artificial intelligence", "analytics", "statistics"],
        "required_skills": ["Python", "Machine Learning", "Statistics", "SQL", "Data Visualization"],
        "demand_score": 92,
        "growth_score": 90,
        "avg_salary_lpa": 14.0,
        "streams": ["CSE", "IT", "Mathematics", "Statistics"],
        "min_marks": 60.0,
    },
    {
        "name": "Cybersecurity Analyst",
        "keywords": ["cyber", "security", "ethical hacking", "network", "infosec"],
        "required_skills": ["Networking", "Linux", "Ethical Hacking", "Python", "Risk Assessment"],
        "demand_score": 88,
        "growth_score": 85,
        "avg_salary_lpa": 11.0,
        "streams": ["CSE", "IT", "Electronics"],
        "min_marks": 55.0,
    },
    {
        "name": "Cloud Engineer",
        "keywords": ["cloud", "aws", "azure", "devops", "infrastructure"],
        "required_skills": ["AWS/Azure", "Linux", "Docker", "Kubernetes", "Networking"],
        "demand_score": 90,
        "growth_score": 87,
        "avg_salary_lpa": 13.0,
        "streams": ["CSE", "IT", "ECE"],
        "min_marks": 55.0,
    },
    {
        "name": "Mechanical Engineer",
        "keywords": ["mechanical", "manufacturing", "automobile", "design", "cad"],
        "required_skills": ["CAD", "Thermodynamics", "Fluid Mechanics", "AutoCAD", "Problem Solving"],
        "demand_score": 72,
        "growth_score": 60,
        "avg_salary_lpa": 6.5,
        "streams": ["Mechanical", "Manufacturing", "Automobile"],
        "min_marks": 50.0,
    },
    {
        "name": "Civil Engineer",
        "keywords": ["civil", "construction", "infrastructure", "building", "structural"],
        "required_skills": ["AutoCAD", "Structural Analysis", "Project Management", "Surveying"],
        "demand_score": 68,
        "growth_score": 58,
        "avg_salary_lpa": 5.5,
        "streams": ["Civil", "Construction", "Infrastructure"],
        "min_marks": 50.0,
    },
    {
        "name": "Electrical Engineer",
        "keywords": ["electrical", "power", "electronics", "control systems", "circuits"],
        "required_skills": ["Circuit Design", "Power Systems", "MATLAB", "PLC", "Embedded Systems"],
        "demand_score": 74,
        "growth_score": 65,
        "avg_salary_lpa": 7.0,
        "streams": ["EEE", "ECE", "Electrical"],
        "min_marks": 50.0,
    },
    {
        "name": "Doctor (MBBS)",
        "keywords": ["medical", "doctor", "medicine", "health", "clinical", "mbbs", "biology"],
        "required_skills": ["Biology", "Chemistry", "Patient Care", "Anatomy", "Diagnostics"],
        "demand_score": 85,
        "growth_score": 78,
        "avg_salary_lpa": 8.0,
        "streams": ["Biology", "Medical", "Science"],
        "min_marks": 70.0,
    },
    {
        "name": "Chartered Accountant",
        "keywords": ["accounting", "finance", "ca", "audit", "commerce", "tax"],
        "required_skills": ["Accounting", "Taxation", "Auditing", "Tally", "Financial Analysis"],
        "demand_score": 80,
        "growth_score": 72,
        "avg_salary_lpa": 9.0,
        "streams": ["Commerce", "Accounting", "Finance"],
        "min_marks": 55.0,
    },
    {
        "name": "UX/UI Designer",
        "keywords": ["design", "ux", "ui", "user experience", "product design", "graphic"],
        "required_skills": ["Figma", "User Research", "Wireframing", "CSS", "Design Thinking"],
        "demand_score": 82,
        "growth_score": 80,
        "avg_salary_lpa": 9.5,
        "streams": ["Design", "CSE", "Arts", "Media"],
        "min_marks": 45.0,
    },
    {
        "name": "AI/ML Engineer",
        "keywords": ["ai", "artificial intelligence", "deep learning", "neural", "nlp", "machine learning"],
        "required_skills": ["Python", "TensorFlow/PyTorch", "Mathematics", "Machine Learning", "Data Processing"],
        "demand_score": 97,
        "growth_score": 95,
        "avg_salary_lpa": 18.0,
        "streams": ["CSE", "IT", "Mathematics", "ECE"],
        "min_marks": 65.0,
    },
    {
        "name": "Business Analyst",
        "keywords": ["business", "analyst", "management", "mba", "strategy", "operations"],
        "required_skills": ["Data Analysis", "Communication", "Excel", "SQL", "Project Management"],
        "demand_score": 84,
        "growth_score": 76,
        "avg_salary_lpa": 10.0,
        "streams": ["Commerce", "Management", "CSE", "Any"],
        "min_marks": 55.0,
    },
]


def _keyword_match_score(text: str, keywords: list[str]) -> float:
    """Return a 0-1 score for how many career keywords appear in the text."""
    text = text.lower()
    matched = sum(1 for kw in keywords if kw in text)
    return matched / len(keywords)


def _skill_match_ratio(student_skills: list[str], required_skills: list[str]) -> float:
    """Return fraction of required skills the student already has."""
    if not required_skills:
        return 0.0
    student_lower = {s.lower() for s in student_skills}
    matched = sum(1 for rs in required_skills if rs.lower() in student_lower)
    return matched / len(required_skills)


def _marks_eligibility(marks: float, min_marks: float) -> float:
    """Score from 0-1 based on how far above the minimum marks the student is."""
    if marks < min_marks:
        return max(0, 1 - (min_marks - marks) / 50)
    excess = min(marks - min_marks, 40)  # cap at 40 points above minimum
    return 0.6 + 0.4 * (excess / 40)


def score_careers(
    interest_area: str,
    career_goal: str,
    stream: str,
    marks: float,
    student_skills: list[str],
) -> list[dict]:
    """
    Score all careers in the knowledge base. Returns sorted list of:
      {name, score, demand, growth, avg_salary_lpa, skill_match_pct,
       missing_skills, explanation}
    """
    combined_text = f"{interest_area} {career_goal} {stream}".lower()
    results = []

    for career in CAREER_KB:
        # 1. Interest / keyword affinity (0-30 pts)
        kw_score = _keyword_match_score(combined_text, career["keywords"]) * 30

        # 2. Marks eligibility (0-25 pts)
        marks_score = _marks_eligibility(marks, career["min_marks"]) * 25

        # 3. Skill match (0-25 pts)
        skill_ratio = _skill_match_ratio(student_skills, career["required_skills"])
        skill_score = skill_ratio * 25

        # 4. Demand + growth sector momentum (0-20 pts)
        demand_score = ((career["demand_score"] + career["growth_score"]) / 200) * 20

        total = kw_score + marks_score + skill_score + demand_score
        total = round(min(total, 100), 1)  # cap at 100

        # Missing skills
        student_lower = {s.lower() for s in student_skills}
        missing = [rs for rs in career["required_skills"] if rs.lower() not in student_lower]

        # Explanation text
        explanation = (
            f"Matched {round(kw_score / 30 * 100)}% on interest keywords. "
            f"You meet the marks requirement (your {marks}% vs min {career['min_marks']}%). "
            f"You have {round(skill_ratio * 100)}% of the required skills."
        )

        results.append({
            "name": career["name"],
            "score": total,
            "demand": career["demand_score"],
            "growth": career["growth_score"],
            "avg_salary_lpa": career["avg_salary_lpa"],
            "skill_match_pct": round(skill_ratio * 100),
            "missing_skills": missing,
            "explanation": explanation,
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)
