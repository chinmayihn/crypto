# -*- coding: utf-8 -*-
"""
FORENSIQ — FastAPI Backend
POST /analyse  →  full analysis + TinyLlama profile
GET  /health   →  liveness check
"""
 
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json, re
from datetime import datetime
from collections import Counter
 
app = FastAPI(title="FORENSIQ API", version="1.0")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
 
# ── Taxonomy ─────────────────────────────────────────────────
CATEGORY_MAP = {
    "youtube": "Entertainment", "netflix": "Entertainment", "spotify": "Entertainment",
    "twitch": "Entertainment",  "hotstar": "Entertainment", "primevideo": "Entertainment",
    "amazon": "Shopping",       "flipkart": "Shopping",     "myntra": "Shopping",
    "meesho": "Shopping",       "ebay": "Shopping",         "nykaa": "Shopping",
    "linkedin": "Professional", "naukri": "Professional",   "indeed": "Professional",
    "glassdoor": "Professional","internshala": "Professional",
    "github": "Technology",     "stackoverflow": "Technology", "gitlab": "Technology",
    "geeksforgeeks": "Technology", "leetcode": "Technology", "kaggle": "Technology",
    "arxiv": "Research",        "pubmed": "Research",       "scholar": "Research",
    "reddit": "Social",         "instagram": "Social",      "twitter": "Social",
    "facebook": "Social",       "x.com": "Social",          "discord": "Social",
    "bbc": "News",              "cnn": "News",              "reuters": "News",
    "ndtv": "News",             "timesofindia": "News",
    "zerodha": "Finance",       "groww": "Finance",         "binance": "Finance",
    "coinbase": "Finance",      "moneycontrol": "Finance",
    "udemy": "Education",       "coursera": "Education",    "khanacademy": "Education",
    "wikipedia": "Education",   "edx": "Education",
    "openai": "AI Tools",       "claude": "AI Tools",       "gemini": "AI Tools",
    "perplexity": "AI Tools",   "huggingface": "AI Tools",
    "tryhackme": "Cybersecurity", "hackthebox": "Cybersecurity", "owasp": "Cybersecurity",
}
 
SUSPICIOUS_TAXONOMY = {
    "dark web": 3, "exploit kit": 3, "ransomware": 3, "zero day": 3,
    "carding": 3,  "doxxing": 3,
    "hack": 2,     "hacker": 2,     "malware": 2,  "phishing": 2, "ddos": 2,
    "botnet": 2,   "keylogger": 2,  "rootkit": 2,  "trojan": 2,
    "spyware": 2,  "breach": 2,     "bypass": 2,
    "crack": 1,    "keygen": 1,     "torrent": 1,  "piracy": 1,
    "anonymous": 1,"bitcoin": 1,    "virus": 1,    "attack": 1,
}
 
# ── Helpers ──────────────────────────────────────────────────
def _extract_domain(url: str) -> str:
    m = re.search(r"https?://(?:www\.)?([^/?#\s]+)", url)
    return m.group(1).lower() if m else "unknown"
 
def _load_entries(raw: bytes) -> list[dict]:
    try:
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
 
    raw_list = data.get("Browser History", [])
    if not raw_list:
        raise ValueError('No "Browser History" key found in JSON.')
 
    seen, entries = set(), []
    for item in raw_list:
        title = (item.get("title") or "").strip()
        url   = (item.get("url")   or "").strip()
        ts    = item.get("time_usec", 0)
        if not title or not ts:
            continue
        key = f"{title}:{ts}"
        if key in seen:
            continue
        seen.add(key)
        dt = datetime.fromtimestamp(ts / 1_000_000)
        entries.append({
            "title":  title,
            "url":    url,
            "ts":     ts,
            "dt":     dt,
            "hour":   dt.hour,
            "dow":    dt.weekday(),
            "domain": _extract_domain(url),
        })
 
    entries.sort(key=lambda x: x["ts"])
    return entries[:5000]
 
# ── Feature extraction ───────────────────────────────────────
def _interests(entries):
    c = Counter()
    for e in entries:
        text = (e["title"] + " " + e["url"]).lower()
        for kw, cat in CATEGORY_MAP.items():
            if kw in text:
                c[cat] += 1
    return c.most_common()
 
def _suspicious(entries):
    flagged, kw_hits, total = [], Counter(), 0
    for e in entries:
        text = (e["title"] + " " + e["url"]).lower()
        score, kws = 0, []
        for kw, w in SUSPICIOUS_TAXONOMY.items():
            if kw in text:
                score += w; kws.append(kw); kw_hits[kw] += 1
        if score:
            total += score
            flagged.append({
                "dt":       e["dt"].strftime("%Y-%m-%d %H:%M"),
                "title":    e["title"][:80],
                "url":      e["url"],
                "score":    score,
                "keywords": kws,
            })
    return {"flagged": flagged, "totalScore": total, "uniqueCount": len(flagged),
            "kwHits": dict(kw_hits)}
 
def _temporal(entries):
    hourly, daily = Counter(), Counter()
    for e in entries:
        hourly[e["hour"]] += 1
        daily[e["dow"]]   += 1
    total      = len(entries) or 1
    night      = sum(v for h, v in hourly.items() if h <= 4)
    night_pct  = night / total
    peak_hour  = hourly.most_common(1)[0][0] if hourly else 12
    peak_dow   = daily.most_common(1)[0][0]  if daily  else 0
    peak_day   = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][peak_dow]
    behavior   = ("Night-owl"    if night_pct > 0.30 else
                  "Late-evening" if peak_hour >= 20  else
                  "Daytime"      if peak_hour >= 8   else
                  "Early-riser")
    return {
        "hourly":    {str(k): v for k, v in hourly.items()},
        "nightPct":  round(night_pct, 4),
        "peakHour":  peak_hour,
        "peakDay":   peak_day,
        "behavior":  behavior,
    }
 
def _domains(entries):
    c = Counter(e["domain"] for e in entries)
    return c.most_common(15)
 
def _risk(total_score: int) -> str:
    if total_score >= 15: return "Critical"
    if total_score >= 8:  return "High"
    if total_score >= 4:  return "Medium"
    if total_score >= 1:  return "Low"
    return "Minimal"
 
# ── LLM (lazy-loaded on first request) ──────────────────────
_pipe = None
 
def _get_pipe():
    global _pipe
    if _pipe is None:
        from transformers import pipeline as hf_pipeline
        _pipe = hf_pipeline(
            "text-generation",
            model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            device_map="auto",
        )
    return _pipe
 
def _generate_profile(features: dict) -> str:
    top_interests = ", ".join(f"{k} ({v})" for k, v in features["interests"][:5])
    kw_hits_str   = ", ".join(f"{k}×{v}" for k, v in
                               sorted(features["suspicious"]["kwHits"].items(),
                                      key=lambda x: x[1], reverse=True)[:5]) or "None"
    prompt = f"""<|system|>
You are a cybersecurity analyst writing a factual browser-history summary.
 
Strict rules:
- Base every statement ONLY on the numbers provided. Do not invent details.
- If the data does not support a claim, write "Cannot be determined from available data."
- Do NOT guess age or location — there is no data for these.
- Do NOT use dramatic language. Stay concise and neutral.
- Do NOT speculate about intent, personality, or criminal activity.
 
<|user|>
Browser history summary:
- Entries analysed  : {features['total_entries']}
- Date range        : {features['date_range']}
- Top interests     : {top_interests}
- Behaviour pattern : {features['temporal']['behavior']}
- Peak hour         : {features['temporal']['peakHour']:02d}:00  ({features['temporal']['peakDay']})
- Night browsing    : {features['temporal']['nightPct']*100:.1f}%
- Suspicious score  : {features['suspicious']['totalScore']}
- Flagged entries   : {features['suspicious']['uniqueCount']}
- Top keywords hit  : {kw_hits_str}
- Risk level        : {features['risk_level']}
 
Write three short sections:
1. Interest summary (what categories dominate and what that suggests about usage habits)
2. Activity pattern (timing and browsing rhythm, based strictly on the numbers above)
3. Security observation (contextualise the suspicious keyword count — note matches can include legitimate research or news, not only malicious activity)
 
<|assistant|>
"""
    pipe   = _get_pipe()
    result = pipe(prompt, max_new_tokens=400, do_sample=True, temperature=0.3)[0]["generated_text"]
    return result.split("<|assistant|>")[-1].strip()
 
# ── Endpoints ────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}
 
@app.post("/analyse")
async def analyse(file: UploadFile = File(...)):
    raw = await file.read()
 
    try:
        entries = _load_entries(raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
 
    if not entries:
        raise HTTPException(status_code=400, detail="No valid entries found in the file.")
 
    interests  = _interests(entries)
    suspicious = _suspicious(entries)
    temporal   = _temporal(entries)
    top_domains = _domains(entries)
    risk_level  = _risk(suspicious["totalScore"])
 
    fmt = lambda d: d.strftime("%d %b %Y")
    date_range = f"{fmt(entries[0]['dt'])} → {fmt(entries[-1]['dt'])}"
 
    features = {
        "total_entries": len(entries),
        "date_range":    date_range,
        "interests":     interests,
        "suspicious":    suspicious,
        "temporal":      temporal,
        "risk_level":    risk_level,
    }
 
    try:
        profile_text = _generate_profile(features)
    except Exception as e:
        profile_text = f"[LLM unavailable: {e}]"
 
    return {
        "totalEntries": len(entries),
        "dateRange":    date_range,
        "interests":    interests,
        "suspicious":   suspicious,
        "temporal":     temporal,
        "topDomains":   top_domains,
        "riskLevel":    risk_level,
        "profile":      profile_text,
    }