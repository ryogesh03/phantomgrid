import streamlit as st
import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("data/history.json")

st.set_page_config(
    page_title="PhantomGrid",
    page_icon="🛡️",
    layout="wide"
)

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    return []

def save_history(history):
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

def analyze_threat(user_input):
    text = user_input.lower()

    if any(word in text for word in ["password", "verify", "login", "urgent", "bank", "click"]):
        threat_type = "Phishing / Social Engineering"
        risk = "High"
        explanation = "The input contains words commonly found in phishing attempts."
    elif any(word in text for word in ["rm -rf", "sudo", "powershell", "curl", "wget", "chmod"]):
        threat_type = "Suspicious Command"
        risk = "High"
        explanation = "The input contains command-line patterns that may be used in attacks."
    elif any(word in text for word in ["failed login", "multiple attempts", "brute force"]):
        threat_type = "Brute-force Login Attempt"
        risk = "Medium"
        explanation = "The input suggests repeated login attempts or unauthorized access behavior."
    elif any(word in text for word in ["http://", "https://", ".exe", "download"]):
        threat_type = "Suspicious URL / File"
        risk = "Medium"
        explanation = "The input contains links or downloadable file indicators."
    else:
        threat_type = "Unknown / Low Confidence"
        risk = "Low"
        explanation = "No strong threat pattern was detected, but manual review is recommended."

    return threat_type, risk, explanation

def generate_decoy_log(threat_type, risk):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""
[PHANTOMGRID DECOY LOG]
Timestamp: {timestamp}
Threat Type: {threat_type}
Risk Level: {risk}
Action Taken: Decoy environment activated
Decoy Asset: fake-admin-panel.internal
Attacker View: Simulated low-value system exposed
Real System Status: Protected
Response: Suspicious activity redirected to deception layer
"""

st.title("🛡️ PhantomGrid")
st.subheader("AI Cyber Deception Agent")
st.write("Analyze suspicious cyber inputs and generate safe decoy logs for deception-based defense.")

tab1, tab2 = st.tabs(["Threat Analyzer", "Detection History"])

with tab1:
    user_input = st.text_area(
        "Paste suspicious email, URL, command, or login attempt:",
        height=180
    )

    if st.button("Analyze Threat"):
        if not user_input.strip():
            st.warning("Please enter some suspicious input first.")
        else:
            threat_type, risk, explanation = analyze_threat(user_input)
            decoy_log = generate_decoy_log(threat_type, risk)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Threat Analysis")
                st.write(f"**Threat Type:** {threat_type}")
                st.write(f"**Risk Level:** {risk}")
                st.write(f"**Explanation:** {explanation}")

            with col2:
                st.markdown("### Generated Decoy Log")
                st.code(decoy_log)

            history = load_history()
            history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "input": user_input,
                "threat_type": threat_type,
                "risk": risk,
                "explanation": explanation,
                "decoy_log": decoy_log
            })
            save_history(history)

with tab2:
    st.markdown("### Previous Detections")
    history = load_history()

    if not history:
        st.info("No detections yet.")
    else:
        for item in reversed(history):
            with st.expander(f"{item['timestamp']} — {item['threat_type']} — {item['risk']}"):
                st.write("**Input:**")
                st.code(item["input"])
                st.write("**Explanation:**")
                st.write(item["explanation"])
                st.write("**Decoy Log:**")
                st.code(item["decoy_log"])
