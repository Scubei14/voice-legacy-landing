'use client';
import { useState } from "react"; import { http } from "@/lib/api"; import { useRouter } from "next/navigation";
export default function NewPersona(){
  const r=useRouter(); const [name,setName]=useState(""); const [voice_provider,setProvider]=useState("elevenlabs");
  const [traits,setTraits]=useState('{"personality":"gentle, warm"}');
  async function submit(e:React.FormEvent){ e.preventDefault();
    try{ await http.post("/api/personas/", {name, voice_provider, traits: JSON.parse(traits||"{}")}); r.push("/dashboard"); }
    catch(e:any){ alert(e?.response?.data?.detail || "Failed"); } }
  return (<div className="max-w-lg mx-auto card">
    <h1 className="text-2xl font-semibold mb-4">New Persona</h1>
    <form onSubmit={submit} className="space-y-3">
      <input className="input" placeholder="Name (e.g., Mom)" value={name} onChange={e=>setName(e.target.value)} />
      <label className="text-sm opacity-70">Provider</label>
      <select className="input" value={voice_provider} onChange={e=>setProvider(e.target.value)}>
        <option value="elevenlabs">ElevenLabs</option>
      </select>
      <label className="text-sm opacity-70">Traits (JSON)</label>
      <textarea className="input h-40" value={traits} onChange={e=>setTraits(e.target.value)} />
      <button className="btn w-full">Create</button>
    </form>
  </div>); }
