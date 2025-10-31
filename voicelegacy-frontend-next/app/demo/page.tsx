'use client'; import Link from "next/link";
export default function Demo(){
  const has = typeof window!=="undefined" && !!localStorage.getItem("token");
  return (<div className="max-w-2xl mx-auto card space-y-4">
    <h1 className="text-2xl font-semibold">Live Demo</h1>
    <p className="opacity-80">This demo uses your authenticated session to open a WebSocket with continuous voice activity detection.</p>
    {!has ? <div className="opacity-80 text-sm">You need to <Link className="underline" href="/register">create an account</Link> first.</div>
           : <div className="opacity-80 text-sm">Go to your <Link className="underline" href="/dashboard">Dashboard</Link>, create a Persona, then click Talk.</div>}
  </div>);
}
