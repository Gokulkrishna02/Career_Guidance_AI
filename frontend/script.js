const API = "http://127.0.0.1:8000";

// CREATE PROFILE
async function createProfile() {
  const data = {
    name: name.value,
    education_level: "School",
    class_or_degree: "12th",
    stream: "Science",
    marks: parseFloat(marks.value),
    category: category.value,
    interest_area: interest.value,
    location_preference: "Tamil Nadu",
    career_goal: "Job"
  };

  const res = await fetch(`${API}/student-profile`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });

  const result = await res.json();
  studentResult.innerText = "Student ID: " + result.student_id;
}

// RECOMMENDATIONS
async function getRecommendation() {
  const res = await fetch(`${API}/personalized-recommendation/${studentId.value}`);
  const data = await res.json();

  recommendationCards.innerHTML = "";
  data.recommendations.forEach(r => {
    recommendationCards.innerHTML += `
      <div class="reco-card">
        <b>${r.college}</b><br>
        Cutoff: ${r.cutoff}<br>
        Avg Package: ${r.avg_package_lpa} LPA<br>
        Placement: ${r.placement_percentage}%
      </div>`;
  });
}

// CHAT
async function chatAI() {
  const msg = chatMessage.value;
  chatBox.innerHTML += `<div class="user">${msg}</div>`;

  const res = await fetch(`${API}/chat/${chatStudentId.value}?message=${encodeURIComponent(msg)}`, {
    method: "POST"
  });

  const data = await res.json();
  chatBox.innerHTML += `<div class="bot">${data.reply}</div>`;
  chatMessage.value = "";
}

