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


---

## ⚙️ Installation

### 1. Install Python
Download from: https://www.python.org/downloads/

---

### 2. Install dependencies

```bash
python -m pip install streamlit pandas plotly python-dotenv
3. Run the app
python -m streamlit run app1.py
🔑 API Setup (Optional - for AI profiling)
Step 1: Get API Key
Visit: https://console.anthropic.com
Generate API key
Step 2: Create .env file
ANTHROPIC_API_KEY=your_api_key_here
Step 3: Enable AI in sidebar

Toggle:

🤖 Enable AI Profile (Claude)
📊 Input Format
✅ Chrome JSON
{
  "Browser History": [
    {
      "title": "Example",
      "url": "https://example.com",
      "time_usec": 1710345435804090
    }
  ]
}
✅ Text File
2024-03-13 15:21:45: YouTube Video
https://github.com
📄 Output
Behavioral profile
Risk assessment
Interest analysis charts
Suspicious activity logs
AI-generated psychological report
Downloadable report
🧠 Methodology
Preprocessing
Extract titles, URLs, timestamps
Categorization
Map domains to interest categories
Behavior Detection
Time-based pattern analysis
Threat Detection
Regex-based suspicious keyword matching
Risk Scoring
Based on severity and frequency
AI Profiling
LLM generates psychological insights
Evaluation
Compare predictions with heuristic ground truth
⚠️ Limitations
Ground truth is heuristic-based (not labeled data)
AI profiling depends on API availability
Suspicious detection relies on keyword matching
🔮 Future Improvements
Real-time browser tracking
Advanced ML models for classification
Improved location detection
User authentication system
Better UI animations
💬 Conclusion

This project demonstrates how browser history can be leveraged to:

Understand user behavior
Detect cybersecurity risks
Generate AI-driven insights

It combines rule-based logic with AI to create a hybrid intelligent system.

👩‍💻 Author

Chinmayi 

Acknowledgements
Streamlit
Plotly
Anthropic (Claude API)
