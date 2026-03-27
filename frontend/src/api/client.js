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

  // Local dev: support testing from other devices on the same LAN.
  if (host && !isLocalHost && isIpv4Host) {
    return `http://${host}:8000/api`;
  }

  // Production fallback without env var: call same-origin /api.
  // This works when frontend and backend are served behind a single domain.
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

// ─── Emotion Detection ───
export const detectEmotion = (imageBase64, userId) =>
  API.post("/emotion/detect", { image: imageBase64, user_id: userId });

// ─── Voice ───
export const transcribeVoice = (formData) =>
  API.post("/voice/transcribe", formData);

// ─── Mood Tracker ───
export const logMood = (mood, note, userId) =>
  API.post("/mood", { user_id: userId, mood, note });
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

export default API;
