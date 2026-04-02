import axios from "axios";

function normalizeBaseUrl(url) {
  let u = String(url || "").trim().replace(/\/+$/, "");
  if (u && !u.endsWith("/api")) {
    u += "/api";
  }
  return u;
}

// Resolve backend URL for local and deployed environments.
function getApiBase() {
  const envUrl = normalizeBaseUrl(import.meta.env.VITE_API_URL);
  if (envUrl) return envUrl;

  const host = window.location.hostname;
  const isLocalHost = host === "localhost" || host === "127.0.0.1";
  const isIpv4Host = /^(\d{1,3}\.){3}\d{1,3}$/.test(host);

  if (host && !isLocalHost && isIpv4Host) {
    return `http://${host}:8000/api`;
  }

  if (!isLocalHost) {
    return "/api";
  }

  return "http://localhost:8000/api";
}

export const API_BASE = getApiBase();

const API = axios.create({ baseURL: API_BASE });

// Attach JWT token to every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("mindcare_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ─── Auth ───
export const registerUser = (name, email, password) =>
  API.post("/auth/register", { name, email, password });
export const loginUser = (email, password) =>
  API.post("/auth/login", { email, password });
export const getMe = () => API.get("/auth/me");

// ─── Chat ───
export const sendMessage = (message, userId, therapistMode = true) =>
  API.post("/chat", { message, user_id: userId, therapist_mode: therapistMode });
export const getChatHistory = (userId) =>
  API.get(`/chat/history?user_id=${userId}`);
export const clearChatHistory = (userId) =>
  API.delete(`/chat/history?user_id=${userId}`);
export const getSessionHistory = (userId, limit = 5) =>
  API.get(`/chat/sessions?user_id=${userId}&limit=${limit}`);

// ─── Voice ───
export const transcribeVoice = (formData) =>
  API.post("/voice/transcribe", formData);

// ─── Mood Tracker ───
export const logMood = (mood, note, userId, moodScore = null, sleepHours = null, energyLevel = null) =>
  API.post("/mood", { user_id: userId, mood, note, mood_score: moodScore, sleep_hours: sleepHours, energy_level: energyLevel });
export const getMoods = (userId, range = "week") =>
  API.get(`/mood?user_id=${userId}&range=${range}`);

// ─── Wellness ───
export const getWellnessTips = () => API.get("/wellness/tips");
export const getMotivation = () => API.get("/wellness/motivation");
export const getEmergency = () => API.get("/wellness/emergency");

// ─── Smart Alerts ───
export const getAlerts = (userId) => API.get(`/alerts?user_id=${userId}`);

// ─── Follow-Up System ───
export const getFollowUps = (userId) => API.get(`/followup?user_id=${userId}`);
export const checkIn = (userId) => API.post(`/followup/checkin?user_id=${userId}`);
export const getStreak = (userId) => API.get(`/followup/streak?user_id=${userId}`);
export const markFollowUpRead = (id) => API.put(`/followup/read/${id}`);

// ─── Analytics & Dashboard ───
export const getDashboardStats = (userId) => API.get(`/analytics/dashboard?user_id=${userId}`);
export const getMoodAnalytics = (userId, days = 30) => API.get(`/analytics/mood?user_id=${userId}&days=${days}`);
export const getEmotionAnalytics = (userId, days = 30) => API.get(`/analytics/emotions?user_id=${userId}&days=${days}`);
export const getChatAnalytics = (userId) => API.get(`/analytics/chat?user_id=${userId}`);
export const getRecommendations = (userId, mood = "") => API.get(`/analytics/recommendations?user_id=${userId}&mood=${mood}`);
export const getPersonalizedGreeting = (userId, name = "") => API.get(`/analytics/greeting?user_id=${userId}&name=${name}`);

// ─── Assessments (PHQ-9 / GAD-7) ───
export const getAssessmentQuestions = (type) => API.get(`/assessment/questions/${type}`);
export const submitPHQ9 = (userId, answers) => API.post("/assessment/phq9", { user_id: userId, answers });
export const submitGAD7 = (userId, answers) => API.post("/assessment/gad7", { user_id: userId, answers });
export const getPHQ9History = (userId) => API.get(`/assessment/phq9/history?user_id=${userId}`);
export const getGAD7History = (userId) => API.get(`/assessment/gad7/history?user_id=${userId}`);
export const getAssessmentTrends = (userId) => API.get(`/assessment/trends?user_id=${userId}`);

// ─── Homework (CBT Loop) ───
export const assignHomework = (userId, category = "", emotion = "") =>
  API.post("/homework/assign", { user_id: userId, category, emotion });
export const getHomework = (userId, status = "") =>
  API.get(`/homework?user_id=${userId}&status=${status}`);
export const completeHomework = (homeworkId, note = "", rating = 3) =>
  API.post("/homework/complete", { homework_id: homeworkId, completion_note: note, rating });
export const skipHomework = (homeworkId) => API.post(`/homework/skip/${homeworkId}`);
export const getHomeworkStats = (userId) => API.get(`/homework/stats?user_id=${userId}`);

// ─── Admin Dashboard ───
export const getAdminOverview = () => API.get("/admin/overview");
export const getAdminUsers = (limit = 50) => API.get(`/admin/users?limit=${limit}`);
export const getHighRiskUsers = () => API.get("/admin/high-risk");
export const getUserRisk = (userId) => API.get(`/admin/risk/${userId}`);
export const getCrisisEvents = (limit = 50) => API.get(`/admin/crisis-events?limit=${limit}`);
export const getAdminAlerts = () => API.get("/admin/alerts");
export const acknowledgeAlert = (alertId) => API.post(`/admin/alerts/${alertId}/acknowledge`);
export const resolveAlert = (alertId) => API.post(`/admin/alerts/${alertId}/resolve`);
export const getUserDetail = (userId) => API.get(`/admin/user-detail/${userId}`);
export const getRetentionStats = () => API.get("/admin/retention");
export const getPHQ9Distribution = () => API.get("/admin/phq9-distribution");
export const getWeeklySummary = () => API.get("/admin/weekly-summary");

// ─── GDPR ───
export const updateConsent = (userId, consentType, granted) =>
  API.post("/gdpr/consent", { user_id: userId, consent_type: consentType, granted });
export const getConsents = (userId) => API.get(`/gdpr/consent?user_id=${userId}`);
export const exportUserData = (userId) => API.get(`/gdpr/export?user_id=${userId}`);
export const deleteUserData = (userId) => API.delete(`/gdpr/delete?user_id=${userId}`);

export default API;
