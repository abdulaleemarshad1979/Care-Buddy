# 🩺 CareBuddy – AI Medical Q&A Assistant

> **Your trusted AI health companion powered by Groq LLaMA 3.3 70B**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-Educational-green)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Deploy to Streamlit Cloud](#deploy-to-streamlit-cloud)
- [Multi-Language Support](#multi-language-support)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Disclaimer](#disclaimer)

---

## Overview

CareBuddy is a production-grade AI health assistant built with **Streamlit** and **Groq's LLaMA 3.3 70B**. It allows users to chat with an AI about health questions, upload medical reports for analysis, check symptoms, and manage medication reminders — all in multiple languages.

---

## Features

| Feature | Details |
|---|---|
| 💬 **AI Chat** | Groq LLaMA 3.3 70B – fast and accurate health Q&A |
| 🌐 **Multi-Language** | English, Hindi, Telugu, Español, Français |
| 📄 **PDF Extraction** | Upload medical reports as PDF for AI analysis |
| 🖼️ **Image OCR** | Image reports processed via OCR.space API |
| 🔬 **Symptom Checker** | AI analysis with severity gauge and emergency flags |
| 💊 **Medication Reminders** | Add, view, and delete daily reminders with time sorting |
| 🌙 **Dark Mode** | Full dark/light theme toggle |
| 💾 **Chat Download** | Export full chat history as `.txt` |
| 🕐 **Recent Searches** | Clickable sidebar chips showing last 5 questions |
| 💡 **Quick Questions** | Suggestion chips for new users |
| 🔒 **Scope Guard** | AI refuses non-medical questions |

---

## Tech Stack

- **Frontend & Backend** — [Streamlit](https://streamlit.io)
- **AI Model** — [Groq API](https://console.groq.com) — LLaMA 3.3 70B Versatile
- **PDF Parsing** — [pdfplumber](https://github.com/jsvine/pdfplumber)
- **Image OCR** — [OCR.space API](https://ocr.space)
- **Image Processing** — [Pillow](https://python-pillow.org)
- **HTTP Requests** — [requests](https://requests.readthedocs.io)

---

## Project Structure

```
carebuddy/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .gitignore              # Excludes secrets and cache
├── README.md               # This file
└── .streamlit/
    └── secrets.toml        # API keys (DO NOT commit this file)
```

---

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Free Groq API key → [console.groq.com/keys](https://console.groq.com/keys)
- Free OCR.space API key → [ocr.space/ocrapi/freekey](https://ocr.space/ocrapi/freekey)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/carebuddy.git
cd carebuddy

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create secrets file
mkdir -p .streamlit
```

Create `.streamlit/secrets.toml` and add your keys:

```toml
GROQ_API_KEY = "gsk_your_groq_key_here"
```

```bash
# 5. Run the app
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## Deploy to Streamlit Cloud

This is the **easiest and completely free** way to deploy.

### Step 1 — Push to GitHub

```bash
git init
git add app.py requirements.txt .gitignore README.md
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/carebuddy.git
git push -u origin main
```

### Step 2 — Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **New app**
4. Select your repository, branch `main`, and main file `app.py`
5. Click **Advanced settings → Secrets** and paste:

```toml
GROQ_API_KEY = "gsk_your_groq_key_here"
```

6. Click **Deploy** — your app will be live in ~60 seconds ✅

Your app URL will be:
```
https://YOUR_USERNAME-carebuddy.streamlit.app
```

---

## Multi-Language Support

CareBuddy supports 5 languages out of the box:

| Language | Code |
|---|---|
| English | `English` |
| Hindi | `हिन्दी (Hindi)` |
| Telugu | `తెలుగు (Telugu)` |
| Spanish | `Español` |
| French | `Français` |

The AI automatically responds in the selected language via the system prompt.

### Adding a New Language

1. Open `app.py`
2. Find the `TRANSLATIONS` dictionary
3. Copy the `"English"` block and rename the key (e.g. `"Deutsch"`)
4. Translate all the string values
5. The new language will automatically appear in the sidebar dropdown

---

## Configuration

| Setting | Location | Default |
|---|---|---|
| AI Model | `app.py → call_api()` | `llama-3.3-70b-versatile` |
| Max Tokens | `app.py → call_api()` | `700` |
| Temperature | `app.py → call_api()` | `0.4` |
| Request Timeout | `app.py → call_api()` | `30 seconds` |
| Max Upload Size | Streamlit default | `10 MB` |
| Recent Searches | `app.py` | `5 items` |
| OCR Engine | `app.py → extract_image()` | `OCR Engine 2` |
| Image Compression | `app.py → compress_image()` | `Auto (max 900 KB)` |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `KeyError: 'GROQ_API_KEY'` | Add your Groq key to `.streamlit/secrets.toml` |
| Blank screen on load | Check terminal for Python errors; ensure `streamlit>=1.35` |
| PDF text is empty | PDF may be image-only; upload as image instead |
| OCR failed: file size limit | App auto-compresses images; try a smaller file if it persists |
| API returns 401 | Invalid or expired Groq key; regenerate at console.groq.com |
| API returns 429 | Rate limit hit; wait a moment and retry |
| Dark mode not applying fully | Hard refresh browser with `Ctrl + Shift + R` |

---

## Disclaimer

CareBuddy is built for **educational purposes only**. It is **not a medical device** and does **not** provide professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for medical concerns.
