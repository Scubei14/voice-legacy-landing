"use client";

import { useEffect, useState } from "react";
import { http } from "@/lib/api";

export default function Dashboard() {
  const [health, setHealth] = useState<string>("…");

  useEffect(() => {
    async function run() {
      try {
        const res = await http.get("/health");
        setHealth("UP: " + JSON.stringify(res.data));
      } catch (e: any) {
        setHealth("DOWN: " + (e?.message || e));
      }
    }
    run();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Dashboard</h1>
      <div className="border rounded-xl p-4">
        <div className="text-sm">Backend health:</div>
        <pre className="mt-2 text-sm whitespace-pre-wrap">{health}</pre>
      </div>
    </div>
  );
}
