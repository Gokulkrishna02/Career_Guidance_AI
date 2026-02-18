function openProfile() {
  profileModal.style.display = "flex";
}

function closeProfile() {
  profileModal.style.display = "none";
}

async function saveProfile() {
  alert("Profile updated");
  closeProfile();
}
