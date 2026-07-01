# PhantomGrid

**Turning deception into defense**

PhantomGrid is an AI-powered cyber deception agent built for the AMD Developer Hackathon. It detects suspicious cyber inputs, explains possible risks, and generates safe decoy/honeypot logs to simulate a deception-based cyber defense layer.

## Live Demo

https://phantomgrid-ipu65t3kjzgij3uujeqbse.streamlit.app/

## Problem Statement

Cyber threats such as phishing emails, suspicious commands, malicious URLs, and brute-force login attempts are difficult to analyze quickly, especially for students, small teams, and early-stage security learners.

Traditional security tools often show alerts, but they may not explain the risk clearly or demonstrate how deception-based defense can slow down attackers.

## Solution

PhantomGrid provides a simple cyber deception interface where users can paste suspicious input and receive:

- Threat classification
- Risk score
- Plain-English explanation
- Generated decoy/honeypot log
- Detection history dashboard

The project demonstrates how AI-assisted cyber defense and deception concepts can be used to improve security awareness and incident response.

## Key Features

- Suspicious email, URL, command, and login log analysis
- Rule-based threat detection engine
- Risk level and risk score generation
- Safe decoy/honeypot response generation
- Detection history dashboard
- Sample inputs for quick demo
- Professional Streamlit-based interface
- Future-ready structure for AI/LLM integration

## Tech Stack

- Python
- Streamlit
- Regex/rule-based detection
- JSON-based local history storage
- GitHub
- Streamlit Community Cloud

## How It Works

1. User enters suspicious cyber input.
2. PhantomGrid scans the input using rule-based threat patterns.
3. The system classifies the input into categories such as phishing, suspicious command, brute-force login attempt, or suspicious URL/file.
4. A risk score and explanation are generated.
5. A safe decoy/honeypot-style log is produced.
6. Detection history is stored locally for dashboard viewing.

## Threat Categories

- Phishing / Social Engineering
- Suspicious Command
- Brute-force Login Attempt
- Suspicious URL / File
- Unknown / Low Confidence

## Screenshots

Add screenshots here after uploading them to the repository.

## Run Locally

```bash
pip install streamlit
python -m streamlit run app.py
