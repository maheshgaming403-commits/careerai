const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function token() {
  return localStorage.getItem("careerai_token");
}

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
        ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
        ...options.headers,
      },
    });
    clearTimeout(timeout);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      return { success: false, message: data.detail || data.message || `Request failed (${res.status})` };
    }
    return data;
  } catch (err) {
    clearTimeout(timeout);
    if (err.name === "AbortError") {
      return { success: false, message: "Request timed out. Please try again." };
    }
    return { success: false, message: "Network error. Check your connection and try again." };
  }
}

export const api = {
  signup: (body) => request("/api/auth/signup", { method: "POST", body: JSON.stringify(body) }),
  login: (body) => request("/api/auth/login", { method: "POST", body: JSON.stringify(body) }),
  health: () => request("/health"),
  analyzeResume: (formData) => request("/api/resume/analyze", { method: "POST", body: formData }),
  analyzeSkills: (skills) => request("/api/skills/analyze", { method: "POST", body: JSON.stringify({ skills }) }),
  matchJobs: (payload) => request("/api/job/match", { method: "POST", body: JSON.stringify(payload) }),
  generateRoadmap: (payload) => request("/api/roadmap/generate", { method: "POST", body: JSON.stringify(payload) }),
  recommendProjects: (skillGap) => request("/api/projects/recommend", { method: "POST", body: JSON.stringify({ skillGap }) }),
  startInterview: (role) => request("/api/interview/start", { method: "POST", body: JSON.stringify({ role }) }),
  evaluateAnswer: (payload) => request("/api/interview/evaluate", { method: "POST", body: JSON.stringify(payload) }),
};
