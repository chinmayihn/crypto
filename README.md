# 🕵️ AI Behavioral Intelligence System

An AI-powered cybersecurity and behavioral profiling system that analyzes browser history to generate psychological insights, detect suspicious activity, and assess risk levels.

---

## 🚀 Overview

This project processes browser history data (Chrome JSON or text format) and performs:

- 📊 Behavioral analysis  
- 🧠 Interest detection  
- 🛡️ Cybersecurity risk assessment  
- 🤖 AI-based psychological profiling  
- 📈 Evaluation against ground truth  

The system visualizes results through an interactive Streamlit dashboard.

---

## ✨ Features

### 🔍 Data Processing
- Parses Chrome browser history (`History.json`)
- Supports plain `.txt` browsing logs
- Extracts timestamps, domains, and titles

### 🧠 Behavioral Analysis
- Identifies user interests (technology, entertainment, etc.)
- Detects usage patterns (Night Owl, Early Bird, etc.)
- Finds peak browsing hours

### 🛡️ Cybersecurity Detection
- Flags suspicious activities:
  - Hacking attempts
  - Dark web usage
  - Phishing
  - Malware-related searches
- Assigns risk levels:
  - Low / Medium / High

### 🤖 AI Profiling (Optional)
- Uses Claude API (Anthropic) to generate:
  - Psychological profile
  - Age range estimation
  - Behavioral insights
  - Risk reasoning

### 📊 Visualization Dashboard
- Interactive charts (interests, activity by hour)
- Risk indicators and metrics
- Suspicious activity logs
- Clean UI with dark theme

### 📈 Evaluation System
- Compares predictions with ground truth
- Calculates accuracy scores for:
  - Age
  - Interests
  - Location

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** (Frontend + Backend)
- **Pandas** (Data processing)
- **Plotly** (Charts)
- **Regex** (Pattern detection)
- **Claude API (optional)**

---

## 📂 Project Structure


project/
│
├── app1.py # Main Streamlit application
├── .env # API keys (optional)
├── README.md


