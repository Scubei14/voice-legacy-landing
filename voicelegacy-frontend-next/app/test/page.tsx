"use client";

import React, { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function TestPage() {
  const [out, setOut] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  async function goHealth() {
    try {
      const res = await fetch(`${API}/health`);
      const txt = await res.text();
      setOut(`STATUS ${res.status}\n\n${txt}`);
    } catch (e: any) {
      setOut("Network error: " + (e?.message || e));
    }
  }

  async function doRegister() {
    try {
      const payload = {
        email: email || `john+${Math.floor(Math.random() * 1e6)}@example.com`,
        password: password || "Password123!",
        display_name: "John Test",
      };
      const res = await fetch(`${API}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const txt = await res.text();
      setOut(`REGISTER STATUS ${res.status}\n\n${txt}`);
    } catch (e: any) {
      setOut("Network error: " + (e?.message || e));
    }
  }

  async function doLogin() {
    try {
      const payload = {
        email,
        password,
      };
      const res = await fetch(`${API}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const txt = await res.text();
      setOut(`LOGIN STATUS ${res.status}\n\n${txt}`);
    } catch (e: any) {
      setOut("Network error: " + (e?.message || e));
    }
  }

  return (
    <div className="min-h-screen bg-white text-black p-6">
      <h1 className="text-2xl font-semibold mb-4">API Test</h1>

      <div className="grid gap-3 max-w-lg">
        <div>
          <label className="block text-sm mb-1">Email</label>
          <input
            className="w-full rounded border border-gray-300 px-3 py-2 bg-white text-black"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="username"
          />
        </div>

        <div>
          <label className="block text-sm mb-1">Password</label>
          <input
            className="w-full rounded border border-gray-300 px-3 py-2 bg-white text-black"
            placeholder="Password123!"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </div>

        <div className="flex gap-2">
          <button onClick={goHealth} className="px-3 py-2 rounded bg-black text-white">
            GET /health
          </button>
          <button onClick={doRegister} className="px-3 py-2 rounded bg-black text-white">
            POST /auth/register
          </button>
          <button onClick={doLogin} className="px-3 py-2 rounded bg-black text-white">
            POST /auth/login
          </button>
        </div>
      </div>

      <pre className="mt-6 bg-gray-100 text-black p-3 rounded whitespace-pre-wrap">
        {out}
      </pre>
    </div>
  );
}
