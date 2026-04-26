"""
Vercel entry-point for CareBuddy.

NOTE: Streamlit is NOT natively supported on Vercel's serverless platform.
The recommended free hosting options for Streamlit apps are:
  1. Streamlit Community Cloud  → https://share.streamlit.io  (easiest, free)
  2. Railway                    → https://railway.app          (free tier)
  3. Render                     → https://render.com           (free tier)

If you MUST deploy to Vercel, convert the app to FastAPI + HTMX or Next.js.
This file is a placeholder that redirects visitors to the Streamlit Cloud URL.
"""

def handler(request, response):
    response.status_code = 302
    response.headers["Location"] = "https://carebuddy.streamlit.app"
    return response
