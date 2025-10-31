
import axios, { AxiosRequestConfig } from "axios";

// Prefer env, but fall back to the backend container name on the shared network.
const API_BASE =
  (typeof window !== "undefined"
    ? (window as any).NEXT_PUBLIC_API_URL
    : process.env.NEXT_PUBLIC_API_URL) || "http://voicelegacy-backend:8000";

export const http = axios.create({
  baseURL: API_BASE,
  withCredentials: false,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach bearer token if present (keep TS happy re: headers type)
http.interceptors.request.use((config: AxiosRequestConfig) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (token) {
    (config.headers ??= {}) as any;
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});
