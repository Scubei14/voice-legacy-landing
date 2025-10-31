
"use client";

import React, { useState } from "react";
import { http } from "@/lib/api";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    setBusy(true);
    try {
      // Backend expects EXACT keys: { email, password, display_name }
      const res = await http.post("/api/auth/register", {
        email,
        password,
        display_name: displayName || undefined,
      });
      const data = res.data as {
        access_token: string;
        refresh_token: string;
        token_type: string;
      };
      localStorage.setItem("access_token", data.access_token);
      setMsg("✅ Registered! Token stored. Redirecting to dashboard…");
      window.location.href = "/dashboard";
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Registration failed";
      setMsg(`❌ ${detail}`);
      console.error("REGISTER ERROR:", err?.response?.data || err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6">
      <div className="w-full max-w-md rounded-2xl shadow p-6 bg-white/90 dark:bg-neutral-900/90">
        <h1 className="text-2xl font-semibold mb-4">Create account</h1>

        <form onSubmit={onSubmit} className="space-y-4">
          <label className="block">
            <span className="text-sm">Display name (optional)</span>
            <input
              className="mt-1 w-full rounded-xl border px-3 py-2 bg-white text-black dark:bg-neutral-800 dark:text-white"
              placeholder="John"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </label>

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
              placeholder="Min 8 chars, with upper/lower/number"
              type="password"
              autoComplete="new-password"
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
            {busy ? "Creating…" : "Create account"}
          </button>
        </form>

        <div className="mt-4 text-sm">
          {msg && <div>{msg}</div>}
        </div>
      </div>
    </div>
  );
}
