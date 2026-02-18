function toggle() {
  document.getElementById("register").style.display = "block";
}

async function login() {
  const res = await api("/auth/login", "POST", {
    email: email.value,
    password: password.value
  });
  if (res.student_id) {
    localStorage.setItem("student_id", res.student_id);
    location.href = "index.html";
  }
}

async function register() {
  await api("/auth/register", "POST", {
    name: name.value,
    email: email.value,
    password: password.value
  });
  alert("Registered. Login now.");
}
