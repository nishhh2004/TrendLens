---
title: TrendLens
emoji: ⚡
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.44.1
app_file: dashboard.py
pinned: false
license: mit
---

# ⚡ TrendLens - Growth Intelligence & AI Strategy Engine

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat&logo=python) ![Data Science](https://img.shields.io/badge/Data-Science-orange?style=flat) ![NLP](https://img.shields.io/badge/NLP-Sentiment-yellow?style=flat) ![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-red?style=flat&logo=streamlit) ![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)

---

## 📌 Problem Statement

In the modern creator economy, content strategy is often based on guesswork rather than data. Creators and agencies struggle to scale because:
* 📉 **Lack of predictive insights** leads to inconsistent viewership.
* 💬 **Audience sentiment is ignored**, missing the actual "struggles" viewers relate to.
* ❌ **Trends are caught too late** instead of being forecasted before they peak.

**TrendLens** solves this by using data pipelines and machine learning to analyze:
* ✅ **Virality** (Algorithmic push vs. engagement)
* 🧠 **Sentiment** (What makes audiences feel understood)
* 🔮 **Momentum** (What external topics are surging right now)

---

## 🚀 Solution

**TrendLens** is an **AI-powered data pipeline and web application** that allows content strategists to:
* **Extract & Process** historical video performance and thousands of user comments.
* **Analyze** human emotion and relatability using Natural Language Processing (NLP).
* **Visualize** exactly which topics and title formats drive the highest viral coefficients.
* **Forecast** breakout topics using real-time search momentum.

The system uses a highly structured Python backend to feed a dynamic, dark-mode Streamlit dashboard.

---

## ✨ Features

* 🎯 **The Virality Matrix:** Scatter plot correlation of emotional resonance vs. algorithmic push.
* 💬 **NLP Problem Awareness:** Automated tagging of audience comments (Relatable, Neutral, Venting).
* 🧪 **A/B Testing Framework:** Statistical breakdown of Title Lengths and Hook Strategies.
* 🤖 **Prescriptive AI Strategy:** Generates a blueprint for the next upload based on the top 15% of historical performers.
* 🌍 **Live Trend Forecasting:** Gracefully handles Google Trends API to predict surging topics.

---

## 📁 Folder Structure

```text
TrendLens/
│
├── .streamlit/
│   └── config.toml                  # UI Customization & Dark Mode Theme
│
├── datasets/
│   ├── Comment_Sentiment_Logs.csv   # NLP processed audience data
│   └── Video_Analytics.csv          # Cleaned video performance metrics
│
├── ab_testing_framework.py          # Module 4: Structural format testing
├── dashboard.py                     # Module 6: Main Streamlit Application
├── recommender_engine.py            # Module 5: AI Strategy Generator
├── sentiment_analyzer.py            # Module 3: NLP Comment Classification
├── trend_forecaster.py              # Module 7: Live Google Trends integration
├── virality_engine.py               # Module 2: Viral Coefficient Calculator
├── youtube_data_collector.py        # Module 1: YouTube API Extraction
├── youtube_data.db                  # Local SQLite Database
├── requirements.txt                 # Project dependencies
└── README.md                        # Project documentation

```

## 💻 How to Run Locally

Follow these steps to set up TrendLens on your local machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/TrendLens.git](https://github.com/YOUR_USERNAME/TrendLens.git)
   cd TrendLens

2. **Set up a Virtual Environment (Recommended):**
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Mac/Linux
   python3 -m venv .venv
   source .venv/bin/activate

3. **Install dependencies:**
   pip install -r requirements.txt

4. **Configure Environment Variables:**
   Create a .env file in the root directory.
   Add your YouTube API Key: YOUTUBE_API_KEY=your_key_here

5. **Initialize the Data Pipeline:**
   Ensure youtube_data_collector.py has been run to populate the local database.

6. **Launch the Intelligence Dashboard:**
   streamlit run dashboard.py