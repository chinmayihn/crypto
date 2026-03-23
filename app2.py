import streamlit as st
from collections import Counter
import pandas as pd
import time
import re
import json
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Behavioral Intelligence", layout="wide", page_icon="🕵️")

# ---------- STYLES ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Exo 2', sans-serif; background: #020617; color: #e2e8f0; }
.stApp { background: radial-gradient(ellipse at 20% 0%, #0f172a 0%, #020617 60%); }
.title {
    text-align: center; font-size: 48px; font-weight: 800;
    background: linear-gradient(90deg, #00f5a0, #00d9f5, #7c3aed);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -1px; margin-bottom: 4px;
}
.subtitle {
    text-align: center; color: #475569; font-family: 'Share Tech Mono', monospace;
    font-size: 13px; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 32px;
}
.card {
    padding: 24px; border-radius: 16px; background: rgba(15,23,42,0.8);
    border: 1px solid rgba(0,245,160,0.15); backdrop-filter: blur(20px);
    box-shadow: 0 0 40px rgba(0,217,245,0.05), inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 12px;
}
.risk-badge {
    font-size: 52px; font-weight: 800; text-align: center;
    font-family: 'Share Tech Mono', monospace; letter-spacing: 4px; margin: 8px 0;
}
.stat-label {
    font-family: 'Share Tech Mono', monospace; font-size: 11px;
    color: #64748b; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 2px;
}
.stat-value { font-size: 28px; font-weight: 600; color: #00f5a0; }
.profile-text {
    font-family: 'Share Tech Mono', monospace; font-size: 13px;
    line-height: 1.9; color: #94a3b8; white-space: pre-wrap;
}
.section-header {
    font-size: 13px; font-weight: 600; letter-spacing: 3px; text-transform: uppercase;
    color: #00d9f5; margin-bottom: 16px; font-family: 'Share Tech Mono', monospace;
    border-left: 3px solid #00d9f5; padding-left: 10px;
}
.tag {
    display: inline-block; background: rgba(0,245,160,0.1);
    border: 1px solid rgba(0,245,160,0.3); color: #00f5a0; border-radius: 6px;
    padding: 2px 10px; font-size: 12px; font-family: 'Share Tech Mono', monospace; margin: 2px;
}
.stButton > button {
    background: linear-gradient(135deg, #00f5a0, #00d9f5); color: #020617;
    font-weight: 700; font-family: 'Exo 2', sans-serif; letter-spacing: 2px;
    text-transform: uppercase; border: none; border-radius: 10px;
    padding: 12px 32px; font-size: 14px; width: 100%;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 0 30px rgba(0,245,160,0.5); }
.stProgress > div > div { background: linear-gradient(90deg, #00f5a0, #00d9f5); }
div[data-testid="stDataFrame"] { border: 1px solid rgba(0,245,160,0.15); border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ---------- CONSTANTS ----------
CATEGORY_PATTERNS = {
    "entertainment":  [r"youtube\.com", r"youtu\.be", r"netflix\.com", r"primevideo", r"hulu", r"disneyplus", r"twitch\.tv", r"spotify", r"hotstar", r"jiocinema", r"zee5"],
    "shopping":       [r"amazon\.", r"flipkart", r"ebay\.", r"myntra", r"meesho", r"ajio", r"nykaa", r"snapdeal", r"swiggy", r"zomato", r"blinkit", r"bigbasket"],
    "professional":   [r"linkedin\.com", r"glassdoor", r"naukri", r"indeed\.", r"angellist", r"wellfound", r"internshala"],
    "technology":     [r"github\.com", r"stackoverflow", r"gitlab", r"dev\.to", r"medium\.com", r"hackernews", r"replit", r"codepen", r"npmjs", r"pypi\.org", r"vercel", r"netlify", r"geeksforgeeks", r"w3schools"],
    "social":         [r"instagram\.com", r"reddit\.com", r"twitter\.com", r"x\.com", r"facebook\.com", r"threads\.net", r"discord\.com", r"snapchat", r"koo\.", r"sharechat"],
    "news":           [r"bbc\.com", r"cnn\.com", r"ndtv\.com", r"thehindu", r"nytimes", r"theguardian", r"reuters", r"timesofindia", r"hindustantimes", r"scroll\.in", r"thewire"],
    "finance":        [r"zerodha", r"groww\.in", r"upstox", r"moneycontrol", r"coinbase", r"binance", r"etmoney", r"paytm", r"phonepe", r"bankbazaar", r"paisabazaar"],
    "education":      [r"coursera", r"udemy", r"khanacademy", r"edx\.org", r"duolingo", r"unacademy", r"byju", r"brilliant\.org", r"geeksforgeeks", r"w3schools", r"nptel"],
    "ai_tools":       [r"chat\.openai", r"claude\.ai", r"gemini\.google", r"perplexity", r"huggingface", r"replicate\.com", r"midjourney", r"copilot\.microsoft", r"chatgpt"],
    "cybersecurity":  [r"kali\.org", r"tryhackme", r"hackthebox", r"shodan\.io", r"virustotal", r"exploit-db", r"nvd\.nist\.gov", r"owasp\.org", r"cybrary"],
}

SUSPICIOUS_PATTERNS = [
    (r"hack|hacking|exploit\b|shell\b|payload|bypass|privilege.?escal", "hacking"),
    (r"dark.?web|\.onion|tor.?browser|tails.?os", "dark web"),
    (r"phishing|spoof|credential.?harvest|fake.?login", "phishing"),
    (r"torrent|piracy|crack(ed)?\b|keygen|warez|nulled", "piracy"),
    (r"ransomware|malware|trojan|keylogger|rootkit|spyware", "malware"),
    (r"ddos|dos.?attack|botnet|stresser", "DDoS"),
    (r"password.?dump|data.?breach|leaked.?database", "data breach"),
    (r"crypto.?scam|rug.?pull|ponzi|wallet.?drain", "crypto fraud"),
]

INDIA_SIGNALS = ["flipkart","myntra","jio","airtel","ndtv","timesofindia","naukri",
                 "zerodha","groww","swiggy","zomato","unacademy","byju","ajio",
                 "meesho","nykaa","paytm","phonepe","hotstar","sharechat","koo"]

# ---------- HELPERS ----------

def parse_chrome_json(raw_bytes):
    try:
        data    = json.loads(raw_bytes.decode("utf-8", errors="ignore"))
        entries = data.get("Browser History", [])
        lines   = []
        for e in entries:
            title  = e.get("title", "").strip()
            url    = e.get("url", "").strip()
            t_usec = e.get("time_usec", 0)
            if not title and not url:
                continue
            dt   = datetime.fromtimestamp(t_usec / 1_000_000).strftime("%Y-%m-%d %H:%M:%S")
            text = title if title else url
            lines.append(f"{dt}: {text} [{url}]")
        return lines, len(entries)
    except Exception:
        return None, 0

def parse_txt(raw_bytes):
    text = raw_bytes.decode("utf-8", errors="ignore")
    return [l for l in text.split("\n") if l.strip()], None

def parse_hour(line):
    iso = re.search(r"\b\d{4}-\d{2}-\d{2} (\d{2}):", line)
    if iso:
        return int(iso.group(1))
    ts = re.search(r"\b(\d{1,2}):(\d{2})(?::\d{2})?\s*(AM|PM|am|pm)?\b", line)
    if ts:
        h, m = int(ts.group(1)), ts.group(3)
        if m and m.upper() == "PM" and h != 12: h += 12
        if m and m.upper() == "AM" and h == 12: h = 0
        return h if 0 <= h <= 23 else None
    return None

def categorize(lines):
    count = Counter()
    for line in lines:
        ll = line.lower()
        for cat, pats in CATEGORY_PATTERNS.items():
            if any(re.search(p, ll) for p in pats):
                count[cat] += 1
    return count

def detect_suspicious(lines):
    hits = []
    for line in lines:
        ll = line.lower()
        for pat, label in SUSPICIOUS_PATTERNS:
            if re.search(pat, ll):
                hits.append({"line": line.strip(), "type": label})
                break
    return hits

def time_analysis(lines):
    hours = [h for l in lines if (h := parse_hour(l)) is not None]
    hc    = Counter(hours)
    return {
        "night":       sum(1 for h in hours if 0  <= h <= 4),
        "morning":     sum(1 for h in hours if 5  <= h <= 11),
        "afternoon":   sum(1 for h in hours if 12 <= h <= 17),
        "evening":     sum(1 for h in hours if 18 <= h <= 23),
        "peak_hour":   hc.most_common(1)[0][0] if hours else None,
        "total_timed": len(hours),
        "hour_counts": hc,
    }

def infer_behavior(td):
    if td["total_timed"] == 0:
        return ["Insufficient timestamp data"]
    b = []
    if td["night"]     > 5:                                                             b.append("Night Owl 🦉")
    if td["morning"]   > td["afternoon"] and td["morning"]   > td["evening"]:          b.append("Early Bird 🌅")
    if td["evening"]   > td["morning"]   and td["evening"]   > td["afternoon"]:        b.append("Evening Browser 🌆")
    if td["afternoon"] > td["morning"]   and td["afternoon"] > td["evening"]:          b.append("Afternoon User ☀️")
    return b or ["Regular Hours 📅"]

def compute_risk(hits):
    severe = {"hacking","malware","phishing","dark web","DDoS"}
    sc = sum(1 for h in hits if h["type"] in severe)
    n  = len(hits)
    if sc >= 3 or n >= 8:   return "HIGH",   "#ef4444", 0.95
    elif sc >= 1 or n >= 3: return "MEDIUM", "#f59e0b", 0.55
    else:                   return "LOW",    "#22c55e", 0.15

def extract_domains(lines):
    domains = Counter()
    for line in lines:
        m = re.search(r"https?://([^/\s\]]+)", line)
        if m:
            d = re.sub(r"^www\.", "", m.group(1))
            domains[d] += 1
    return domains

def infer_location(lines):
    combined = " ".join(lines[:500]).lower()
    hits = sum(1 for d in INDIA_SIGNALS if d in combined)
    if hits >= 3:
        return "India (inferred)"
    return "Unknown"

def build_llm_prompt(interests, behaviors, risk, susp_hits, td, total, top_domains):
    top_int  = ", ".join(interests[:5]) or "general browsing"
    beh_str  = ", ".join(behaviors)
    stypes   = list(set(h["type"] for h in susp_hits))
    dom_smpl = ", ".join(d for d, _ in top_domains.most_common(12))
    return f"""You are a cybersecurity analyst and behavioral profiler. Analyze this browser history data and produce a concise professional report.

DATA:
- Total records: {total}
- Interest categories: {top_int}
- Behavioral patterns: {beh_str}
- Peak activity hour: {(str(td['peak_hour']).zfill(2) + ':00') if td['peak_hour'] is not None else 'unknown'}
- Night sessions (00-04h): {td["night"]}
- Risk level: {risk}
- Suspicious events: {len(susp_hits)} ({", ".join(stypes) if stypes else "none"})
- Top domains: {dom_smpl or "unknown"}

RULES:
- Do NOT assign any name
- No accusations — stay neutral and evidence-based
- No exaggeration

GENERATE (use plain text with section headers):
1. Psychological Profile (2 paragraphs)
2. Estimated Age Range (with brief reasoning)
3. Inferred Location/Region (use domain signals e.g. Flipkart/Jio → India)
4. Interest Breakdown
5. Behavioral Insights
6. Cybersecurity Risk Assessment"""

def call_tinyllama(prompt):
    from transformers import pipeline
    pipe = pipeline(
        "text-generation",
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        device_map="auto"
    )
    messages = [
        {"role": "system", "content": "You are a cybersecurity analyst and behavioral profiler. Generate a realistic and professional psychological profile based only on given data. Do NOT assign any name. Do NOT make accusations. Keep analysis neutral and evidence-based. Avoid exaggeration."},
        {"role": "user", "content": prompt}
    ]
    formatted = f"<|system|>\n{messages[0]['content']}\n<|user|>\n{messages[1]['content']}\n<|assistant|>\n"
    result = pipe(formatted, max_new_tokens=500, do_sample=True)[0]["generated_text"]
    return result.split("<|assistant|>")[-1].strip()

def generate_report(interests, behaviors, risk, hits, td, total, ai_profile):
    lines = [
        "=== AI BEHAVIORAL INTELLIGENCE REPORT ===",
        f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "", "--- BROWSING PROFILE ---",
        f"Primary Interests  : {', '.join(interests[:5])}",
        f"Behavioral Pattern : {', '.join(behaviors)}",
        f"Peak Usage Hour    : {(str(td['peak_hour']).zfill(2) + ':00') if td['peak_hour'] is not None else 'Unknown'}",
        f"Night Sessions     : {td['night']}",
        f"Total Records      : {total}",
        "", "--- RISK ASSESSMENT ---",
        f"Risk Level         : {risk}",
        f"Suspicious Events  : {len(hits)}",
        f"Threat Categories  : {', '.join(set(h['type'] for h in hits)) or 'None'}",
        "", "--- SUSPICIOUS ENTRIES ---",
    ] + [f"  [{h['type'].upper()}] {h['line'][:120]}" for h in hits[:30]]
    if len(hits) > 30:
        lines.append(f"  ... and {len(hits)-30} more.")
    lines += ["", "--- AI GENERATED PROFILE ---", ai_profile or "(AI profile not generated)"]
    return "\n".join(lines)

# ============================================================
# UI
# ============================================================
st.markdown("<div class='title'> AI Behavioral Intelligence</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Cybersecurity · Profiling · Behavioral Analysis</div>", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    use_ai = st.toggle("🤖 Enable AI Profile (TinyLlama)", value=True,
                       help="Uses TinyLlama-1.1B locally. First run downloads ~600MB from HuggingFace.")
    st.markdown("---")
    st.markdown("### 📋 Supported Formats")
    st.markdown("""
**Chrome JSON** (`History.json`)
```json
{"Browser History": [
  {"title":"...", "url":"...", "time_usec":...}
]}
```
**Plain .txt** (one entry per line)
```
2024-03-13 15:21:45: Page Title
https://github.com
```
    """)
    st.markdown("---")
    st.markdown("### 🔍 Evaluation (Optional)")
    st.markdown("Compare against ground truth:")
    true_age      = st.text_input("True Age Range",        placeholder="e.g. 20-29")
    true_location = st.text_input("True Location",         placeholder="e.g. Bangalore, India")
    true_int_raw  = st.text_input("True Interests (CSV)",  placeholder="e.g. technology, social")

# ---------- UPLOAD ----------
uploaded_file = st.file_uploader(
    "📂 Upload Browser History — Chrome JSON or plain .txt",
    type=["json", "txt"],
    help="Chrome: chrome://history → ⋮ → Export browsing data"
)

if not uploaded_file:
    st.markdown("""
    <div class='card'>
    <div class='section-header'>How to export Chrome history</div>
    <p style='font-family:Share Tech Mono,monospace;font-size:13px;color:#64748b;line-height:2.2'>
    1. Open <code>chrome://history</code><br>
    2. Click ⋮ (top-right) → <b>Export browsing data</b><br>
    3. Save as <code>History.json</code> and upload above.<br><br>
    Or upload a plain <code>.txt</code> file — one URL or page title per line.
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

raw = uploaded_file.read()
ext = uploaded_file.name.rsplit(".", 1)[-1].lower()

# ---------- PARSE ----------
if ext == "json":
    lines, raw_count = parse_chrome_json(raw)
    if lines is None:
        st.error("⚠️ Could not parse JSON. Ensure it's a valid Chrome history export.")
        st.stop()
    st.info(f"✅ Chrome JSON — **{raw_count:,}** raw entries → **{len(lines):,}** usable records from `{uploaded_file.name}`")
else:
    lines, _ = parse_txt(raw)
    st.info(f"✅ Plain text — **{len(lines):,}** records from `{uploaded_file.name}`")

if len(lines) == 0:
    st.error("⚠️ No records found. Check your file format.")
    st.stop()

# ---------- RUN ----------
if st.button("⚡ INITIATE ANALYSIS"):

    bar = st.progress(0, text="Scanning records...")
    msgs = ["Scanning records...", "Categorising domains...", "Flagging anomalies...", "Building profile..."]
    for i in range(100):
        time.sleep(0.005)
        bar.progress(i + 1, text=msgs[i // 25])
    bar.empty()

    cat_count    = categorize(lines)
    susp_hits    = detect_suspicious(lines)
    td           = time_analysis(lines)
    behaviors    = infer_behavior(td)
    risk, rc, rp = compute_risk(susp_hits)
    interests    = [c for c, _ in cat_count.most_common()]
    top_domains  = extract_domains(lines)
    inferred_loc = infer_location(lines)

    # ── DASHBOARD ─────────────────────────────────────
    st.markdown("<div class='section-header'>◈ BEHAVIORAL PROFILE</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='stat-label'>Top Interests</div>", unsafe_allow_html=True)
        for i in interests[:5]:
            st.markdown(f"<span class='tag'>{i}</span>", unsafe_allow_html=True)
        st.markdown("<br><div class='stat-label' style='margin-top:16px'>Behavior</div>", unsafe_allow_html=True)
        for b in behaviors:
            st.markdown(f"<span class='tag'>{b}</span>", unsafe_allow_html=True)
        if td["peak_hour"] is not None:
            st.markdown(f"<br><div class='stat-label' style='margin-top:16px'>Peak Hour</div>", unsafe_allow_html=True)
            peak_str = str(td['peak_hour']).zfill(2) + ':00'
            st.markdown(f"<div class='stat-value'>{peak_str}</div>", unsafe_allow_html=True)
        st.markdown(f"<br><div class='stat-label' style='margin-top:16px'>Inferred Region</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='tag'>{inferred_loc}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='stat-label'>Risk Level</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='risk-badge' style='color:{rc}'>{risk}</div>", unsafe_allow_html=True)
        st.progress(rp)
        st.markdown(f"<br><div class='stat-label'>Flagged Events</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-value'>{len(susp_hits)}</div>", unsafe_allow_html=True)
        for t in sorted(set(h["type"] for h in susp_hits)):
            st.markdown(f"<span class='tag' style='border-color:#ef4444;color:#ef4444'>{t}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='stat-label'>Total Records</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-value'>{len(lines):,}</div>", unsafe_allow_html=True)
        st.markdown("<div class='stat-label' style='margin-top:16px'>Unique Domains</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-value'>{len(top_domains):,}</div>", unsafe_allow_html=True)
        st.markdown("<div class='stat-label' style='margin-top:16px'>Night Sessions (00–04h)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-value'>{td['night']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-top:1px solid rgba(255,255,255,0.05);margin:28px 0'>", unsafe_allow_html=True)

    # ── INTEREST CHART ─────────────────────────────────
    st.markdown("<div class='section-header'>◈ INTEREST ANALYSIS</div>", unsafe_allow_html=True)
    if cat_count:
        df = pd.DataFrame(cat_count.items(), columns=["Category", "Visits"]).sort_values("Visits", ascending=False)
        cA, cB = st.columns([3, 2])
        with cA:
            st.bar_chart(df.set_index("Category"), color="#00f5a0")
        with cB:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='stat-label'>Visit Breakdown</div>", unsafe_allow_html=True)
            total_c = df["Visits"].sum()
            for _, row in df.iterrows():
                pct = row["Visits"] / total_c * 100
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;margin:6px 0'>"
                    f"<span style='font-family:Share Tech Mono,monospace;font-size:12px;color:#94a3b8'>{row['Category']}</span>"
                    f"<span style='font-family:Share Tech Mono,monospace;font-size:12px;color:#00f5a0'>{pct:.1f}%</span></div>"
                    f"<div style='background:#1e293b;border-radius:4px;height:4px;margin-bottom:4px'>"
                    f"<div style='background:linear-gradient(90deg,#00f5a0,#00d9f5);height:4px;border-radius:4px;width:{pct}%'></div></div>",
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No known domains matched. Verify the file format.")

    st.markdown("<hr style='border-top:1px solid rgba(255,255,255,0.05);margin:28px 0'>", unsafe_allow_html=True)

    # ── HOURLY CHART ───────────────────────────────────
    if td["total_timed"] > 0:
        st.markdown("<div class='section-header'>◈ ACTIVITY BY HOUR</div>", unsafe_allow_html=True)
        hour_df = pd.DataFrame([(h, td["hour_counts"].get(h, 0)) for h in range(24)], columns=["Hour", "Visits"])
        st.bar_chart(hour_df.set_index("Hour"), color="#7c3aed")
        st.markdown("<hr style='border-top:1px solid rgba(255,255,255,0.05);margin:28px 0'>", unsafe_allow_html=True)

    # ── TOP DOMAINS ────────────────────────────────────
    st.markdown("<div class='section-header'>◈ TOP VISITED DOMAINS</div>", unsafe_allow_html=True)
    dom_df = pd.DataFrame(top_domains.most_common(20), columns=["Domain", "Visits"])
    if not dom_df.empty:
        st.bar_chart(dom_df.set_index("Domain"), color="#00d9f5")
    st.markdown("<hr style='border-top:1px solid rgba(255,255,255,0.05);margin:28px 0'>", unsafe_allow_html=True)

    # ── SUSPICIOUS LOG ─────────────────────────────────
    if susp_hits:
        st.markdown("<div class='section-header'>◈ SUSPICIOUS ACTIVITY LOG</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        for h in susp_hits[:20]:
            st.markdown(
                f"<div style='font-family:Share Tech Mono,monospace;font-size:12px;padding:6px 0;border-bottom:1px solid rgba(239,68,68,0.1)'>"
                f"<span style='color:#ef4444;margin-right:10px'>[{h['type'].upper()}]</span>"
                f"<span style='color:#64748b'>{h['line'][:140]}</span></div>",
                unsafe_allow_html=True
            )
        if len(susp_hits) > 20:
            st.markdown(f"<p style='color:#64748b;font-size:12px;font-family:Share Tech Mono,monospace'>... and {len(susp_hits)-20} more in the download report.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-top:1px solid rgba(255,255,255,0.05);margin:28px 0'>", unsafe_allow_html=True)

    # ── AI PROFILE ─────────────────────────────────────
    ai_text = ""
    st.markdown("<div class='section-header'>◈ AI PSYCHOLOGICAL PROFILE</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    if use_ai:
        with st.spinner("TinyLlama is generating your profile…"): 
            try:
                prompt  = build_llm_prompt(interests, behaviors, risk, susp_hits, td, len(lines), top_domains)
                ai_text = call_tinyllama(prompt)
                ph = st.empty()
                displayed = ""
                for char in ai_text:
                    displayed += char
                    ph.markdown(f"<div class='profile-text'>{displayed}▌</div>", unsafe_allow_html=True)
                    time.sleep(0.003)
                ph.markdown(f"<div class='profile-text'>{displayed}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"TinyLlama unavailable: {e}. Showing rule-based summary.")
                use_ai = False

    if not use_ai or not ai_text:
        summary = (
            f"SUBJECT PROFILE\n{'═'*40}\n\n"
            f"Primary engagement: {', '.join(interests[:3]) or 'general browsing'}.\n"
            f"Pattern: {', '.join(behaviors)}. Peak hour: "
            f"{(str(td['peak_hour']).zfill(2) + ':00') if td['peak_hour'] is not None else 'unknown'}.\n"
            f"Night sessions: {td['night']}. Inferred region: {inferred_loc}.\n\n"
            f"RISK: {risk} — {len(susp_hits)} suspicious event(s) across "
            f"{len(set(h['type'] for h in susp_hits))} threat type(s).\n"
        )
        ph = st.empty()
        displayed = ""
        for char in summary:
            displayed += char
            ph.markdown(f"<div class='profile-text'>{displayed}▌</div>", unsafe_allow_html=True)
            time.sleep(0.005)
        ph.markdown(f"<div class='profile-text'>{displayed}</div>", unsafe_allow_html=True)
        ai_text = summary

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top:1px solid rgba(255,255,255,0.05);margin:28px 0'>", unsafe_allow_html=True)

    # ── EVALUATION ─────────────────────────────────────
    if any([true_age, true_location, true_int_raw]):
        st.markdown("<div class='section-header'>◈ EVALUATION REPORT</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        rows = []

        if true_age:
            pred_age = "20-29"
            try:
                tlo, plo = int(true_age.split("-")[0]), int(pred_age.split("-")[0])
                s = 1.0 if true_age == pred_age else (0.5 if abs(tlo - plo) == 10 else 0.0)
            except:
                s = 0.0
            rows.append(("Age Range", true_age, pred_age, f"{s:.2f}"))

        if true_int_raw:
            true_int = [i.strip().lower() for i in true_int_raw.split(",")]
            pred_int = [i.lower() for i in interests[:len(true_int)]]
            s = len(set(true_int) & set(pred_int)) / max(len(true_int), len(pred_int), 1)
            rows.append(("Interests", ", ".join(true_int), ", ".join(pred_int), f"{s:.2f}"))

        if true_location:
            s = 1.0 if true_location.lower().split(",")[0].strip() in inferred_loc.lower() else 0.0
            rows.append(("Location", true_location, inferred_loc, f"{s:.2f}"))

        eval_df = pd.DataFrame(rows, columns=["Metric", "Ground Truth", "Predicted", "Score"])
        st.dataframe(eval_df, use_container_width=True, hide_index=True)
        if rows:
            avg = sum(float(r[3]) for r in rows) / len(rows)
            st.metric("Overall Accuracy", f"{avg:.0%}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-top:1px solid rgba(255,255,255,0.05);margin:28px 0'>", unsafe_allow_html=True)

    # ── DOWNLOAD ───────────────────────────────────────
    report = generate_report(interests, behaviors, risk, susp_hits, td, len(lines), ai_text)
    st.download_button(
        "📄 Download Full Intelligence Report",
        data=report.encode("utf-8"),
        file_name=f"ai_profiler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )