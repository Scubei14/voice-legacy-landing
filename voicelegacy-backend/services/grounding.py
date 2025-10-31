from __future__ import annotations
from typing import List, Dict, Any
import json

SYSTEM_BASE = ("You are the selected persona. Stay consistent with traits and memories. "
               "Respond empathetically and clearly. Prefer concise, natural phrasing.")

def build_messages(persona_traits: dict, history: List[Dict[str,str]], user_text: str | None,
                   vector_hits: List[Dict[str,Any]], emotions: List[Dict[str,float]]) -> List[Dict[str,str]]:
    def fmt_traits(tr: dict) -> str: return json.dumps(tr or {}, ensure_ascii=False)
    def cards(hits): return "\n".join(f"- {h.get('text','').strip()}" for h in hits[:8] if (h.get('text') or '').strip())
    messages = [{"role":"system","content": SYSTEM_BASE + "\nPersona traits: " + fmt_traits(persona_traits)}]
    if history: messages.extend(history[-6:])
    c = cards(vector_hits)
    if c: messages.append({"role":"system","content":"Relevant memories:\n"+c})
    top = (emotions or [{}])[0].get("label","neutral")
    style = persona_traits.get("speaking_style") or "natural"
    messages.append({"role":"system","content": f"Tone: {top}. Speak in a {style} manner."})
    if user_text: messages.append({"role":"user","content": user_text})
    return messages
