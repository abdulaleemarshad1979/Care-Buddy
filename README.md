# 🩺 CareBuddy – AI Medical Q&A Assistant

> **Production-grade health companion powered by Groq LLaMA 3.3 70B**

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Bug Fixes & Improvements](#bug-fixes--improvements)
4. [Architecture](#architecture)
5. [Quick Start (Local)](#quick-start-local)
6. [Deploy to Streamlit Cloud (Recommended)](#deploy-to-streamlit-cloud)
7. [Deploy via GitHub → Railway / Render](#deploy-via-github--railway--render)
8. [Why Not Vercel?](#why-not-vercel)
9. [Multi-Language Support](#multi-language-support)
10. [Project Structure](#project-structure)
11. [Configuration](#configuration)
12. [Security Notes](#security-notes)
13. [Troubleshooting](#troubleshooting)

---

## Overview

CareBuddy is an AI-powered health assistant built with **Streamlit** and **Groq's LLaMA 3.3 70B**. It lets users:

- Chat with an AI about any health question in **5 languages**
- Upload medical reports (PDF / image) for contextual analysis
- Check symptoms with an AI-powered **Symptom Checker**
- Manage daily **Medication Reminders**
- Switch between **Light and Dark mode**
- Download the full chat history

---

## Features

| Feature | Details |
|---|---|
| 💬 **AI Chat** | Groq LLaMA 3.3 70B – fast, free, accurate |
| 🌐 **Multi-language** | English, Hindi, Telugu, Español, Français |
| 📄 **PDF extraction** | `pdfplumber` – reliable text layer extraction |
| 🖼️ **Image OCR** | `pytesseract` (graceful fallback if unavailable) |
| 🔬 **Symptom Checker** | AI analysis with severity gauge + emergency flags |
| 💊 **Medication Reminders** | Add, view, delete daily reminders with time sorting |
| 🌙 **Dark Mode** | Full dark theme with CSS variable swap |
| 💾 **Chat Download** | Export full history as `.txt` |
| 🕐 **Recent Searches** | Clickable sidebar chips (last 5) |
| 💡 **Quick Questions** | Contextual suggestion chips for new users |
| 🔒 **Scope Guard** | AI refuses non-medical questions |
| ⚠️ **Disclaimer** | Auto-appended in every AI response |

---

## Bug Fixes & Improvements

### 🐛 Bugs Fixed (vs. original `medguide_app.py`)

| # | Bug | Fix |
|---|---|---|
| 1 | `pytesseract` hard crash on servers without Tesseract | Graceful `ImportError` fallback |
| 2 | CSS `float: left/right` bubbles overlap & leak | Proper `flex` layout with `msg-row` |
| 3 | `recent_searches` deque initialized inside cache (state leak) | Moved to `init_state()` |
| 4 | Raw API exceptions shown directly in UI | Caught and formatted as friendly messages |
| 5 | No timeout on API requests (could hang forever) | `timeout=30` on all `requests.post()` |
| 6 | PDF bytes re-read on every Streamlit rerun | `@st.cache_data` on bytes hash |
| 7 | `st.secrets` failure not handled gracefully | Wrapped in `try/except` with clear message |
| 8 | Language not sent to AI (always replied in English) | Language injected into system prompt |
| 9 | Title rendered twice (in `st.title()` AND custom CSS div) | Single topbar renders it |
| 10 | Missing `HTTP-Referer` / `X-Title` headers | Added to all API calls (required by OpenRouter) |
| 11 | OpenRouter deprecated model `llama3-8b-8192` still in code | Migrated to Groq `llama-3.3-70b-versatile` |
| 12 | API key read before `set_page_config` (Streamlit error) | Moved key read inside `call_api()` function |
| 13 | No `ts` key in initial welcome message → KeyError on `msg.get` | All messages created with `ts` field |

### ✨ New Features Added

- **Symptom Checker** tab – structured AI analysis with severity slider
- **Medication Reminders** tab – add/delete/sort reminders by time
- **Dark Mode** toggle – full CSS variable theme swap
- **3-tab navigation** in sidebar (Chat / Symptoms / Reminders)
- **Report status badge** in sidebar and topbar
- **Timestamps** on every message bubble
- **Quick suggestion chips** for new users
- **`config.toml`** brand colors applied globally
- **`.gitignore`** excludes secrets automatically

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Streamlit App                             │
│                                                                  │
│  ┌──────────────────┐   ┌───────────────────────────────────┐   │
│  │     Sidebar       │   │         Main Content              │   │
│  │                  │   │                                   │   │
│  │ • Logo           │   │  Topbar (title + report badge)    │   │
│  │ • Navigation     │   │                                   │   │
│  │ • Language       │   │  Tab: Chat                        │   │
│  │ • Dark Mode      │   │    Message bubbles (flex layout)  │   │
│  │ • Actions        │   │    Suggestion chips               │   │
│  │ • Upload Report  │   │    Chat input                     │   │
│  │ • Recent Queries │   │                                   │   │
│  │ • Disclaimer     │   │  Tab: Symptom Checker             │   │
│  └──────────────────┘   │    Symptoms input + duration      │   │
│                         │    Severity slider + colour gauge │   │
│  Session State:         │    AI analysis result             │   │
│    messages[]           │                                   │   │
│    recent_searches      │  Tab: Medication Reminders        │   │
│    report_text          │    Add reminder form              │   │
│    language             │    Sorted reminder list           │   │
│    dark_mode            │    Delete reminders               │   │
│    active_tab           │                                   │   │
│    reminders[]          └───────────────────────────────────┘   │
│    symptom_result                                                │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS POST (timeout=30s)
                    ┌────────▼─────────┐
                    │   Groq API        │
                    │   LLaMA 3.3 70B  │
                    └──────────────────┘
```

---

## Quick Start (Local)

### Prerequisites
- Python 3.9+
- Free Groq API key → [console.groq.com/keys](https://console.groq.com/keys)
- (Optional) Tesseract OCR for image reports → [Install guide](https://tesseract-ocr.github.io/tessdoc/Installation.html)

### Steps

```bash
# 1. Clone or unzip the project
cd carebuddy

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Open .streamlit/secrets.toml and paste your Groq key:
#   GROQ_API_KEY = "gsk_YOUR_KEY_HERE"

# 5. Run
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## Deploy to Streamlit Cloud

This is the **easiest and free** way to deploy.

1. Push the project to a **GitHub repository**  
   (ensure `.streamlit/secrets.toml` is in `.gitignore` ✅ already done)

2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**

3. Select your repo, branch `main`, and set **Main file path** to `app.py`

4. In **Advanced settings → Secrets**, paste:
   ```toml
   GROQ_API_KEY = "gsk_YOUR_KEY_HERE"
   ```

5. Click **Deploy** — live in ~60 seconds ✅

> **Tesseract on Streamlit Cloud**: Add a `packages.txt` file to enable image OCR:
> ```
> tesseract-ocr
> ```

---

## Deploy via GitHub → Railway / Render

Both platforms support Streamlit natively and offer free tiers.

### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
# Set env var GROQ_API_KEY in the Railway dashboard
```

### Render
1. Create a new **Web Service** from your GitHub repo
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Add env variable `GROQ_API_KEY` in the Render dashboard

---

## Why Not Vercel?

Vercel uses **serverless functions** (max 10s execution, no long-lived processes). Streamlit requires a **persistent server** — the two are incompatible.

| Platform | Streamlit Support | Free Tier | Ease |
|---|---|---|---|
| Streamlit Cloud | ✅ Native | ✅ Yes | ⭐⭐⭐⭐⭐ |
| Railway | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐ |
| Render | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐ |
| Vercel | ❌ No | ✅ Yes | N/A |

---

## Multi-Language Support

Languages are defined in the `TRANSLATIONS` dictionary in `app.py`.

| Language | Key |
|---|---|
| English | `"English"` |
| Hindi | `"हिन्दी (Hindi)"` |
| Telugu | `"తెలుగు (Telugu)"` |
| Spanish | `"Español"` |
| French | `"Français"` |

### Adding a New Language

1. Open `app.py`
2. Copy the `"English"` block inside `TRANSLATIONS`
3. Rename the key (e.g., `"Deutsch"`)
4. Translate all string values
5. The language auto-appears in the sidebar dropdown

The AI responds **in the selected language** automatically via the system prompt.

---

## Project Structure

```
carebuddy/
├── app.py                         # Main Streamlit app (all features)
├── requirements.txt               # Python dependencies
├── vercel.json                    # Vercel config (redirect notice)
├── vercel_app.py                  # Vercel placeholder
├── .gitignore                     # Excludes secrets, venv, cache
├── README.md                      # This file
└── .streamlit/
    ├── config.toml                # Theme + server settings
    └── secrets.toml.example       # API key template (copy → secrets.toml)
```

---

## Configuration

| Setting | File | Default |
|---|---|---|
| API model | `app.py → call_api()` | `llama-3.3-70b-versatile` |
| Max tokens | `app.py → call_api()` | `700` |
| Temperature | `app.py → call_api()` | `0.4` |
| Request timeout | `app.py → call_api()` | `30 s` |
| Max upload size | `.streamlit/config.toml` | `10 MB` |
| Recent searches | `app.py` | `5 items` |

---

## Security Notes

- **Never commit** `.streamlit/secrets.toml` to version control — `.gitignore` already excludes it.
- The API key is read only inside `call_api()` via `st.secrets["GROQ_API_KEY"]` — never exposed to the browser.
- XSRF protection is enabled in `config.toml`.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `KeyError: 'GROQ_API_KEY'` | Create `.streamlit/secrets.toml` with your Groq key |
| Blank screen / white page | Check terminal for Python errors; ensure `streamlit>=1.35` |
| PDF text is empty | PDF may be scanned (image-only); upload as image instead |
| Image OCR not working | Install Tesseract: `sudo apt install tesseract-ocr` |
| API returns 401 | Invalid or expired Groq key; regenerate at console.groq.com |
| API returns 429 | Rate limit hit; wait a moment and retry |
| Slow first response | LLaMA 70B cold-start; subsequent calls are faster |

---

## License

This project is for educational purposes. CareBuddy is **not a medical device** and does not provide medical advice. Always consult a qualified healthcare professional.
