const API = "http://127.0.0.1:8000";

async function api(url, method="GET", body=null) {
  const res = await fetch(API + url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : null
  });
  return res.json();
}
