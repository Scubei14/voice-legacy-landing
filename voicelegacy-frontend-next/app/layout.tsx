import "./globals.css"; import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";
import Toaster from "@/components/Toaster";
export const metadata = { title: "Voice Legacy", description: "Preserve voices. Build legacies. Remember forever." };
export default function RootLayout({ children }:{ children: React.ReactNode }){
  return (<html lang="en"><body><div className="min-h-screen">
    <nav className="sticky top-0 z-50 backdrop-blur bg-black/20 border-b border-white/10">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-6">
        <Link href="/" className="text-lg font-semibold">🔊 Voice Legacy</Link>
        <div className="text-sm opacity-80 hidden md:block">Hands‑free, memory‑aware conversations</div>
        <div className="ml-auto flex items-center gap-3 text-sm">
                <div className="hidden md:block"><ThemeToggle /></div>
          <Link className="btn-secondary" href="/login">Log in</Link>
          <Link className="btn" href="/register">Get Started</Link>
        </div>
      </div>
    </nav>
    <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
    <Toaster />
    <footer className="opacity-60 text-xs text-center py-8">© VoiceLegacy</footer>
  </div></body></html>);
}
