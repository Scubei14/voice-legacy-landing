export default function Home() {
  return (
    <main style={{ minHeight: "100vh", background: "#ffffff", color: "#111", padding: 24 }}>
      <h1 style={{ fontSize: 28, marginBottom: 12 }}>VoiceLegacy — Test Home</h1>
      <p style={{ marginBottom: 24 }}>Use the links below to try auth and the app flow.</p>
      <div style={{ display: "flex", gap: 16 }}>
        <a href="/register" style={{ padding: "10px 16px", border: "1px solid #111", textDecoration: "none" }}>Register</a>
        <a href="/login" style={{ padding: "10px 16px", border: "1px solid #111", textDecoration: "none" }}>Login</a>
        <a href="/dashboard" style={{ padding: "10px 16px", border: "1px solid #111", textDecoration: "none" }}>Dashboard</a>
      </div>
    </main>
  );
}
