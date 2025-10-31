"use client";

import { useParams } from "next/navigation";
import { useEffect } from "react";
import { http } from "@/lib/api";

export default function TalkPage() {
  const params = useParams();
  const personaId = params?.id;

  useEffect(() => {
    console.log("Ready to talk to persona:", personaId);
    // future: fetch `/api/personas/${personaId}` with token if you want
  }, [personaId]);

  return (
    <main style={{ maxWidth: 600, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 600, marginBottom: "1rem" }}>
        Talk Session
      </h1>
      <p>Persona ID: {String(personaId ?? "")}</p>
      <p>Voice chat coming soon.</p>
    </main>
  );
}
