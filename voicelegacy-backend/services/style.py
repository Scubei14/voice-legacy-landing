from typing import Dict, List
EMO_TTS = {"joy":(0.45,0.80),"admiration":(0.50,0.78),"surprise":(0.35,0.85),"anger":(0.65,0.70),
           "sadness":(0.70,0.75),"fear":(0.65,0.72),"neutral":(0.55,0.75)}
def pick_tts_settings(persona_traits: dict, emotions: List[Dict]) -> Dict[str,float]:
    top = (emotions or [{}])[0].get("label","neutral"); stab, sim = EMO_TTS.get(top, EMO_TTS["neutral"])
    personality = (persona_traits or {}).get("personality","").lower()
    if "calm" in personality or "gentle" in personality: stab = min(0.85, stab+0.05)
    if "energetic" in personality or "animated" in personality: stab = max(0.35, stab-0.05)
    return {"stability": float(stab), "similarity_boost": float(sim)}
