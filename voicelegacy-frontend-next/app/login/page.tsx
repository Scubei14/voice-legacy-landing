"use client";

import React, { useState } from "react";
import { http } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    setBusy(true);
    try {
      // Backend expects EXACT keys: { email, password }
      const res = await http.post("/api/auth/login", { email, password });
      const data = res.data as {
        access_token: string;
        refresh_token: string;
        token_type: string;
      };
      localStorage.setItem("access_token", data.access_token);
      setMsg("✅ Logged in! Token stored.");
      // Optional: redirect
      window.location.href = "/dashboard";
    } catch (err: any) {
      // Show the real backend error if provided
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Login failed";
      setMsg(`❌ ${detail}`);
      console.error("LOGIN ERROR:", err?.response?.data || err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6">
      <div className="w-full max-w-md rounded-2xl shadow p-6 bg-white/90 dark:bg-neutral-900/90">
        <h1 className="text-2xl font-semibold mb-4">Sign in</h1>
        <form onSubmit={onSubmit} className="space-y-4">
          <label className="block">
            <span className="text-sm">Email</span>
            <input
              className="mt-1 w-full rounded-xl border px-3 py-2 bg-white text-black dark:bg-neutral-800 dark:text-white"
              placeholder="you@example.com"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>

          <label className="block">
            <span className="text-sm">Password</span>
            <input
              className="mt-1 w-full rounded-xl border px-3 py-2 bg-white text-black dark:bg-neutral-800 dark:text-white"
              placeholder="Your password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>

          <button
            type="submit"
            disabled={busy}
            className="w-full rounded-xl px-4 py-2 border font-medium hover:opacity-90"
          >
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="mt-4 text-sm">
          <div>API Base: <code>{typeof window !== "undefined" ? (window as any).NEXT_PUBLIC_API_URL ?? "" : ""}</code></div>
          {msg && <div className="mt-2">{msg}</div>}
        </div>
      </div>
    </div>
  );
}
