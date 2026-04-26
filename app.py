"""
CareBuddy - AI Medical Q&A Assistant
Production-grade Streamlit application
Features: Multi-language, Symptom Checker, Medication Reminders, Dark Mode, Top Nav Bar
"""

import streamlit as st
import pdfplumber
import requests
import datetime
import json
import base64
from collections import deque
from PIL import Image
import io

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be FIRST Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CareBuddy – AI Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  MULTI-LANGUAGE DICTIONARY
# ─────────────────────────────────────────────
TRANSLATIONS = {
    "English": {
        "page_title": "CareBuddy – AI Health Assistant",
        "app_tagline": "Your trusted AI health companion",
        "welcome_msg": (
            "Hello! I'm **CareBuddy** 👋\n\n"
            "Upload a medical report from the sidebar, or ask me any health-related question. "
            "I'm here to help you understand your health better."
        ),
        "sidebar_language": "🌐 Language",
        "sidebar_actions": "⚙️ Actions",
        "clear_chat": "🗑️ Clear Chat",
        "download_chat": "💾 Download Chat",
        "upload_header": "📂 Upload Report",
        "upload_help": "Upload PDF, PNG, JPG, or JPEG",
        "upload_success": "✅ Report loaded successfully!",
        "upload_empty": "⚠️ No readable text found in the file.",
        "view_text": "📃 View Extracted Text",
        "recent_header": "🕐 Recent Searches",
        "recent_empty": "Your recent questions will appear here.",
        "input_placeholder": "Ask a health question…",
        "thinking": "CareBuddy is thinking…",
        "extraction": "Extracting text from report…",
        "you": "You",
        "carebuddy": "CareBuddy",
        "disclaimer_label": "⚠️ Disclaimer",
        "disclaimer_text": (
            "CareBuddy is for educational purposes only and is **not** a substitute "
            "for professional medical advice. Always consult a qualified healthcare provider."
        ),
        "report_badge": "📄 Report Active",
        "no_report_badge": "📄 No Report",
        "suggestions_label": "💡 Quick Questions",
        "suggestions": [
            "What does high blood pressure mean?",
            "Explain CBC blood test results",
            "What are symptoms of diabetes?",
            "How do I improve my sleep quality?",
        ],
        "error_api": "API error – please check your API key or try again.",
        "error_generic": "Something went wrong. Please try again.",
        "chat_cleared": "Chat cleared! How can I help you today?",
        "symptom_checker": "🔬 Symptom Checker",
        "symptom_input": "Describe your symptoms (comma-separated)…",
        "symptom_duration": "Duration of symptoms",
        "symptom_severity": "Severity (1 = mild, 10 = severe)",
        "analyze_symptoms": "Analyze Symptoms",
        "symptom_result": "Symptom Analysis",
        "symptom_placeholder": "e.g. headache, fever, fatigue",
        "duration_options": ["Less than 1 day", "1–3 days", "4–7 days", "1–2 weeks", "More than 2 weeks"],
        "med_reminder": "💊 Medication Reminders",
        "med_name": "Medication Name",
        "med_dose": "Dosage",
        "med_time": "Reminder Time",
        "add_reminder": "➕ Add Reminder",
        "no_reminders": "No reminders set yet.",
        "delete": "🗑️",
        "reminders_today": "Today's Reminders",
        "dark_mode": "🌙 Dark Mode",
        "light_mode": "☀️ Light Mode",
        "nav_chat": "💬 Chat",
        "nav_symptoms": "🔬 Symptoms",
        "nav_reminders": "💊 Reminders",
    },
    "हिन्दी (Hindi)": {
        "page_title": "CareBuddy – AI स्वास्थ्य सहायक",
        "app_tagline": "आपका विश्वसनीय AI स्वास्थ्य सहायक",
        "welcome_msg": (
            "नमस्ते! मैं **CareBuddy** हूँ 👋\n\n"
            "साइडबार से अपनी मेडिकल रिपोर्ट अपलोड करें या कोई स्वास्थ्य संबंधी प्रश्न पूछें।"
        ),
        "sidebar_language": "🌐 भाषा",
        "sidebar_actions": "⚙️ कार्य",
        "clear_chat": "🗑️ चैट साफ़ करें",
        "download_chat": "💾 चैट डाउनलोड करें",
        "upload_header": "📂 रिपोर्ट अपलोड करें",
        "upload_help": "PDF, PNG, JPG, JPEG अपलोड करें",
        "upload_success": "✅ रिपोर्ट सफलतापूर्वक लोड हुई!",
        "upload_empty": "⚠️ फ़ाइल में पठनीय टेक्स्ट नहीं मिला।",
        "view_text": "📃 निकाला गया टेक्स्ट देखें",
        "recent_header": "🕐 हाल की खोजें",
        "recent_empty": "आपके हाल के प्रश्न यहाँ दिखेंगे।",
        "input_placeholder": "स्वास्थ्य संबंधी प्रश्न पूछें…",
        "thinking": "CareBuddy सोच रहा है…",
        "extraction": "रिपोर्ट से टेक्स्ट निकाला जा रहा है…",
        "you": "आप",
        "carebuddy": "CareBuddy",
        "disclaimer_label": "⚠️ अस्वीकरण",
        "disclaimer_text": "CareBuddy केवल शैक्षणिक उद्देश्यों के लिए है। यह पेशेवर चिकित्सा सलाह का **विकल्प नहीं** है।",
        "report_badge": "📄 रिपोर्ट सक्रिय",
        "no_report_badge": "📄 कोई रिपोर्ट नहीं",
        "suggestions_label": "💡 त्वरित प्रश्न",
        "suggestions": [
            "उच्च रक्तचाप का क्या अर्थ है?",
            "CBC रक्त परीक्षण समझाएं",
            "मधुमेह के लक्षण क्या हैं?",
            "नींद की गुणवत्ता कैसे सुधारें?",
        ],
        "error_api": "API त्रुटि – कृपया अपनी API key जाँचें।",
        "error_generic": "कुछ गलत हो गया। कृपया पुनः प्रयास करें।",
        "chat_cleared": "चैट साफ़ हुई! आज मैं आपकी कैसे मदद कर सकता हूँ?",
        "symptom_checker": "🔬 लक्षण जाँचकर्ता",
        "symptom_input": "अपने लक्षण बताएं (अल्पविराम से अलग करें)…",
        "symptom_duration": "लक्षणों की अवधि",
        "symptom_severity": "गंभीरता (1 = हल्का, 10 = गंभीर)",
        "analyze_symptoms": "लक्षण विश्लेषण करें",
        "symptom_result": "लक्षण विश्लेषण",
        "symptom_placeholder": "उदा. सिरदर्द, बुखार, थकान",
        "duration_options": ["1 दिन से कम", "1–3 दिन", "4–7 दिन", "1–2 सप्ताह", "2 सप्ताह से अधिक"],
        "med_reminder": "💊 दवा अनुस्मारक",
        "med_name": "दवा का नाम",
        "med_dose": "खुराक",
        "med_time": "अनुस्मारक समय",
        "add_reminder": "➕ अनुस्मारक जोड़ें",
        "no_reminders": "अभी कोई अनुस्मारक सेट नहीं।",
        "delete": "🗑️",
        "reminders_today": "आज के अनुस्मारक",
        "dark_mode": "🌙 डार्क मोड",
        "light_mode": "☀️ लाइट मोड",
        "nav_chat": "💬 चैट",
        "nav_symptoms": "🔬 लक्षण",
        "nav_reminders": "💊 अनुस्मारक",
    },
    "తెలుగు (Telugu)": {
        "page_title": "CareBuddy – AI ఆరోగ్య సహాయకుడు",
        "app_tagline": "మీ విశ్వసనీయ AI ఆరోగ్య సహాయకుడు",
        "welcome_msg": (
            "నమస్కారం! నేను **CareBuddy** 👋\n\n"
            "సైడ్‌బార్ నుండి మీ వైద్య నివేదికను అప్‌లోడ్ చేయండి లేదా ఆరోగ్య సంబంధిత ప్రశ్న అడగండి."
        ),
        "sidebar_language": "🌐 భాష",
        "sidebar_actions": "⚙️ చర్యలు",
        "clear_chat": "🗑️ చాట్ క్లియర్",
        "download_chat": "💾 చాట్ డౌన్‌లోడ్",
        "upload_header": "📂 నివేదిక అప్‌లోడ్",
        "upload_help": "PDF, PNG, JPG, JPEG అప్‌లోడ్ చేయండి",
        "upload_success": "✅ నివేదిక విజయవంతంగా లోడ్ అయింది!",
        "upload_empty": "⚠️ ఫైల్‌లో చదవగలిగే వచనం కనుగొనబడలేదు.",
        "view_text": "📃 సేకరించిన వచనం చూడండి",
        "recent_header": "🕐 ఇటీవలి శోధనలు",
        "recent_empty": "మీ ఇటీవలి ప్రశ్నలు ఇక్కడ కనిపిస్తాయి.",
        "input_placeholder": "ఆరోగ్య ప్రశ్న అడగండి…",
        "thinking": "CareBuddy ఆలోచిస్తోంది…",
        "extraction": "నివేదిక నుండి వచనం సేకరిస్తోంది…",
        "you": "మీరు",
        "carebuddy": "CareBuddy",
        "disclaimer_label": "⚠️ నిరాకరణ",
        "disclaimer_text": "CareBuddy కేవలం విద్యా ప్రయోజనాల కోసం మాత్రమే. ఇది వృత్తిపరమైన వైద్య సలహాకు **ప్రత్యామ్నాయం కాదు**.",
        "report_badge": "📄 నివేదిక సక్రియంగా ఉంది",
        "no_report_badge": "📄 నివేదిక లేదు",
        "suggestions_label": "💡 త్వరిత ప్రశ్నలు",
        "suggestions": [
            "అధిక రక్తపోటు అంటే ఏమిటి?",
            "CBC రక్త పరీక్ష ఫలితాలు వివరించండి",
            "మధుమేహం లక్షణాలు ఏమిటి?",
            "నిద్ర నాణ్యత ఎలా మెరుగుపరచాలి?",
        ],
        "error_api": "API లోపం – దయచేసి మీ API కీని తనిఖీ చేయండి.",
        "error_generic": "ఏదో తప్పు జరిగింది. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        "chat_cleared": "చాట్ క్లియర్ అయింది! నేడు నేను మీకు ఎలా సహాయపడగలను?",
        "symptom_checker": "🔬 లక్షణ పరీక్షకుడు",
        "symptom_input": "మీ లక్షణాలు వివరించండి (కామాతో వేరు చేయండి)…",
        "symptom_duration": "లక్షణాల వ్యవధి",
        "symptom_severity": "తీవ్రత (1 = తక్కువ, 10 = తీవ్రం)",
        "analyze_symptoms": "లక్షణాలు విశ్లేషించండి",
        "symptom_result": "లక్షణ విశ్లేషణ",
        "symptom_placeholder": "ఉదా. తలనొప్పి, జ్వరం, అలసట",
        "duration_options": ["1 రోజు కంటే తక్కువ", "1–3 రోజులు", "4–7 రోజులు", "1–2 వారాలు", "2 వారాల కంటే ఎక్కువ"],
        "med_reminder": "💊 మందు రిమైండర్లు",
        "med_name": "మందు పేరు",
        "med_dose": "మోతాదు",
        "med_time": "రిమైండర్ సమయం",
        "add_reminder": "➕ రిమైండర్ జోడించండి",
        "no_reminders": "ఇంకా రిమైండర్లు సెట్ చేయబడలేదు.",
        "delete": "🗑️",
        "reminders_today": "నేటి రిమైండర్లు",
        "dark_mode": "🌙 డార్క్ మోడ్",
        "light_mode": "☀️ లైట్ మోడ్",
        "nav_chat": "💬 చాట్",
        "nav_symptoms": "🔬 లక్షణాలు",
        "nav_reminders": "💊 రిమైండర్లు",
    },
    "Español": {
        "page_title": "CareBuddy – Asistente Médico IA",
        "app_tagline": "Tu compañero de salud IA de confianza",
        "welcome_msg": (
            "¡Hola! Soy **CareBuddy** 👋\n\n"
            "Sube un informe médico desde la barra lateral o hazme cualquier pregunta de salud."
        ),
        "sidebar_language": "🌐 Idioma",
        "sidebar_actions": "⚙️ Acciones",
        "clear_chat": "🗑️ Borrar Chat",
        "download_chat": "💾 Descargar Chat",
        "upload_header": "📂 Subir Informe",
        "upload_help": "Sube PDF, PNG, JPG o JPEG",
        "upload_success": "✅ ¡Informe cargado con éxito!",
        "upload_empty": "⚠️ No se encontró texto legible en el archivo.",
        "view_text": "📃 Ver Texto Extraído",
        "recent_header": "🕐 Búsquedas Recientes",
        "recent_empty": "Tus preguntas recientes aparecerán aquí.",
        "input_placeholder": "Haz una pregunta de salud…",
        "thinking": "CareBuddy está pensando…",
        "extraction": "Extrayendo texto del informe…",
        "you": "Tú",
        "carebuddy": "CareBuddy",
        "disclaimer_label": "⚠️ Descargo de responsabilidad",
        "disclaimer_text": "CareBuddy es solo para fines educativos y **no** reemplaza el consejo médico profesional.",
        "report_badge": "📄 Informe Activo",
        "no_report_badge": "📄 Sin Informe",
        "suggestions_label": "💡 Preguntas Rápidas",
        "suggestions": [
            "¿Qué significa presión arterial alta?",
            "Explica los resultados del análisis CBC",
            "¿Cuáles son los síntomas de la diabetes?",
            "¿Cómo mejorar la calidad del sueño?",
        ],
        "error_api": "Error de API – verifica tu clave API.",
        "error_generic": "Algo salió mal. Inténtalo de nuevo.",
        "chat_cleared": "¡Chat borrado! ¿En qué puedo ayudarte hoy?",
        "symptom_checker": "🔬 Verificador de Síntomas",
        "symptom_input": "Describe tus síntomas (separados por coma)…",
        "symptom_duration": "Duración de los síntomas",
        "symptom_severity": "Gravedad (1 = leve, 10 = grave)",
        "analyze_symptoms": "Analizar Síntomas",
        "symptom_result": "Análisis de Síntomas",
        "symptom_placeholder": "ej. dolor de cabeza, fiebre, fatiga",
        "duration_options": ["Menos de 1 día", "1–3 días", "4–7 días", "1–2 semanas", "Más de 2 semanas"],
        "med_reminder": "💊 Recordatorios de Medicación",
        "med_name": "Nombre del Medicamento",
        "med_dose": "Dosis",
        "med_time": "Hora del Recordatorio",
        "add_reminder": "➕ Agregar Recordatorio",
        "no_reminders": "No hay recordatorios configurados.",
        "delete": "🗑️",
        "reminders_today": "Recordatorios de Hoy",
        "dark_mode": "🌙 Modo Oscuro",
        "light_mode": "☀️ Modo Claro",
        "nav_chat": "💬 Chat",
        "nav_symptoms": "🔬 Síntomas",
        "nav_reminders": "💊 Recordatorios",
    },
    "Français": {
        "page_title": "CareBuddy – Assistant Santé IA",
        "app_tagline": "Votre compagnon santé IA de confiance",
        "welcome_msg": (
            "Bonjour ! Je suis **CareBuddy** 👋\n\n"
            "Téléchargez un rapport médical depuis la barre latérale ou posez-moi une question de santé."
        ),
        "sidebar_language": "🌐 Langue",
        "sidebar_actions": "⚙️ Actions",
        "clear_chat": "🗑️ Effacer le chat",
        "download_chat": "💾 Télécharger le chat",
        "upload_header": "📂 Télécharger un rapport",
        "upload_help": "Téléchargez PDF, PNG, JPG ou JPEG",
        "upload_success": "✅ Rapport chargé avec succès !",
        "upload_empty": "⚠️ Aucun texte lisible trouvé dans le fichier.",
        "view_text": "📃 Voir le texte extrait",
        "recent_header": "🕐 Recherches récentes",
        "recent_empty": "Vos questions récentes apparaîtront ici.",
        "input_placeholder": "Posez une question de santé…",
        "thinking": "CareBuddy réfléchit…",
        "extraction": "Extraction du texte du rapport…",
        "you": "Vous",
        "carebuddy": "CareBuddy",
        "disclaimer_label": "⚠️ Avertissement",
        "disclaimer_text": "CareBuddy est à des fins éducatives uniquement et **ne remplace pas** un avis médical professionnel.",
        "report_badge": "📄 Rapport actif",
        "no_report_badge": "📄 Aucun rapport",
        "suggestions_label": "💡 Questions rapides",
        "suggestions": [
            "Que signifie une tension artérielle élevée ?",
            "Expliquer les résultats d'une prise de sang CBC",
            "Quels sont les symptômes du diabète ?",
            "Comment améliorer la qualité du sommeil ?",
        ],
        "error_api": "Erreur API – vérifiez votre clé API.",
        "error_generic": "Quelque chose s'est mal passé. Veuillez réessayer.",
        "chat_cleared": "Chat effacé ! Comment puis-je vous aider aujourd'hui ?",
        "symptom_checker": "🔬 Vérificateur de Symptômes",
        "symptom_input": "Décrivez vos symptômes (séparés par des virgules)…",
        "symptom_duration": "Durée des symptômes",
        "symptom_severity": "Gravité (1 = léger, 10 = sévère)",
        "analyze_symptoms": "Analyser les Symptômes",
        "symptom_result": "Analyse des Symptômes",
        "symptom_placeholder": "ex. maux de tête, fièvre, fatigue",
        "duration_options": ["Moins d'1 jour", "1–3 jours", "4–7 jours", "1–2 semaines", "Plus de 2 semaines"],
        "med_reminder": "💊 Rappels de Médicaments",
        "med_name": "Nom du Médicament",
        "med_dose": "Dosage",
        "med_time": "Heure du Rappel",
        "add_reminder": "➕ Ajouter un Rappel",
        "no_reminders": "Aucun rappel configuré.",
        "delete": "🗑️",
        "reminders_today": "Rappels d'Aujourd'hui",
        "dark_mode": "🌙 Mode Sombre",
        "light_mode": "☀️ Mode Clair",
        "nav_chat": "💬 Chat",
        "nav_symptoms": "🔬 Symptômes",
        "nav_reminders": "💊 Rappels",
    },
}

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "language": "English",
        "messages": None,
        "recent_searches": deque(maxlen=5),
        "report_text": "",
        "report_name": "",
        "dark_mode": False,
        "active_tab": "chat",
        "reminders": [],
        "symptom_result": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def t(key: str):
    lang = st.session_state.get("language", "English")
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, key)

if st.session_state.messages is None:
    st.session_state.messages = [
        {"role": "bot", "content": t("welcome_msg"), "ts": datetime.datetime.now().strftime("%H:%M")}
    ]

# ─────────────────────────────────────────────
#  THEME TOKENS
# ─────────────────────────────────────────────
dark = st.session_state.dark_mode

if dark:
    BG          = "#0F1117"
    SURFACE     = "#1A1D2E"
    SURFACE2    = "#252840"
    PRIMARY     = "#4D8EFF"
    PRIMARY_SOFT= "#1A2845"
    ACCENT      = "#00C9A7"
    TEXT        = "#E8EAF6"
    TEXT_MUTED  = "#8892B0"
    BORDER      = "#2D3154"
    BOT_BUBBLE  = "#1A1D2E"
    INPUT_BG    = "#1A1D2E"
    DISC_BG     = "#2D2A1A"
    DISC_BORDER = "#5C4A00"
    DISC_TEXT   = "#D4A017"
    CHIP_BG     = "#1A1D2E"
    DANGER      = "#FF6B6B"
    SHADOW      = "0 4px 24px rgba(0,0,0,0.4)"
    NAV_BG      = "#13162A"
    NAV_BORDER  = "#2D3154"
    PILL_ACTIVE = PRIMARY
    PILL_HOVER  = PRIMARY_SOFT
else:
    BG          = "#F0F4FF"
    SURFACE     = "#FFFFFF"
    SURFACE2    = "#F8FAFF"
    PRIMARY     = "#1E6FFF"
    PRIMARY_SOFT= "#EBF1FF"
    ACCENT      = "#00C9A7"
    TEXT        = "#1A1D2E"
    TEXT_MUTED  = "#6B7280"
    BORDER      = "#E2E8F0"
    BOT_BUBBLE  = "#FFFFFF"
    INPUT_BG    = "#FFFFFF"
    DISC_BG     = "#FFFBEB"
    DISC_BORDER = "#FDE68A"
    DISC_TEXT   = "#92400E"
    CHIP_BG     = "#FFFFFF"
    DANGER      = "#FF5C5C"
    SHADOW      = "0 4px 24px rgba(30,111,255,0.08)"
    NAV_BG      = "#FFFFFF"
    NAV_BORDER  = "#E2E8F0"
    PILL_ACTIVE = PRIMARY
    PILL_HOVER  = PRIMARY_SOFT

# ─────────────────────────────────────────────
#  GLOBAL CSS — Aggressive dark mode overrides
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=Sora:wght@600;700;800&display=swap');

:root {{
    --bg: {BG};
    --surface: {SURFACE};
    --surface2: {SURFACE2};
    --primary: {PRIMARY};
    --primary-soft: {PRIMARY_SOFT};
    --accent: {ACCENT};
    --text: {TEXT};
    --text-muted: {TEXT_MUTED};
    --border: {BORDER};
    --shadow: {SHADOW};
    --bot-bubble: {BOT_BUBBLE};
    --user-bubble: linear-gradient(135deg, {PRIMARY} 0%, {"#1A3AB5" if dark else "#0A4FD6"} 100%);
    --input-bg: {INPUT_BG};
    --disclaimer-bg: {DISC_BG};
    --disclaimer-border: {DISC_BORDER};
    --disclaimer-text: {DISC_TEXT};
    --nav-bg: {NAV_BG};
    --nav-border: {NAV_BORDER};
    --danger: {DANGER};
}}

/* ── Hide the decorative HTML nav bar — only the Streamlit button nav is used ── */
.top-nav-bar {{ display: none !important; }}

/* ── Full page reset ── */
html, body {{
    font-family: 'DM Sans', sans-serif !important;
    background-color: {BG} !important;
    color: {TEXT} !important;
}}

/* ── Streamlit root containers — COMPREHENSIVE dark mode ── */
.stApp,
.stApp > div,
.stApp > div > div,
.main,
.main > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > div,
[data-testid="stAppViewContainer"] > div > div,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="block-container"],
.block-container,
section.main,
div[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlock"] > div,
div[data-testid="stVerticalBlockSeparator"],
div[data-testid="column"],
div[data-testid="stColumn"],
div[data-testid="stHorizontalBlock"],
div[data-testid="stForm"],
div[data-testid="stFormSubmitButton"],
.element-container,
.row-widget,
.stMarkdown,
[data-testid="stMarkdownContainer"] {{
    background-color: {BG} !important;
    color: {TEXT} !important;
    font-family: 'DM Sans', sans-serif !important;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
div[data-testid="stDecoration"] {{ display: none; }}
.block-container {{ padding-top: 0 !important; max-width: 100% !important; }}

/* ── Single working nav bar — wraps the Streamlit button columns ── */
div[data-testid="stHorizontalBlock"]:has(button[kind="secondary"]) {{
    background-color: {NAV_BG} !important;
    border-bottom: 1px solid {NAV_BORDER} !important;
    padding: 8px 16px !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
    margin-bottom: 8px !important;
    box-shadow: {SHADOW} !important;
    gap: 8px !important;
}}

/* ── Nav buttons — pill style ── */
div[data-testid="stHorizontalBlock"]:has(button[kind="secondary"]) .stButton > button,
div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]) .stButton > button {{
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 10px 0 !important;
    text-align: center !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div {{
    background-color: {SURFACE} !important;
    border-right: 1px solid {BORDER} !important;
    color: {TEXT} !important;
}}
section[data-testid="stSidebar"] * {{
    color: {TEXT} !important;
}}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCaption {{
    color: {TEXT_MUTED} !important;
}}

/* ── ALL Text elements ── */
p, span, div, h1, h2, h3, h4, h5, h6, li, td, th,
.stMarkdown, .stMarkdown p, .stMarkdown span,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span {{
    color: {TEXT} !important;
}}

/* ── Text inputs ── */
.stTextInput > div > div > input,
.stTextInput input,
input[type="text"],
input[type="number"],
input[type="email"] {{
    background-color: {INPUT_BG} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    caret-color: {PRIMARY} !important;
}}
.stTextInput label {{
    color: {TEXT_MUTED} !important;
    font-size: 13px !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {PRIMARY} !important;
    box-shadow: 0 0 0 3px {"rgba(77,142,255,0.2)" if dark else "rgba(30,111,255,0.15)"} !important;
}}

/* ── Textarea ── */
.stTextArea textarea,
textarea {{
    background-color: {INPUT_BG} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.stTextArea label {{ color: {TEXT_MUTED} !important; }}

/* ── Select / Dropdown ── */
.stSelectbox > div > div,
.stSelectbox [data-baseweb="select"],
.stSelectbox [data-baseweb="select"] > div,
[data-baseweb="select"],
[data-baseweb="select"] > div,
[data-baseweb="popover"],
[data-baseweb="menu"] {{
    background-color: {INPUT_BG} !important;
    color: {TEXT} !important;
    border-color: {BORDER} !important;
    border-radius: 10px !important;
}}
.stSelectbox label {{ color: {TEXT_MUTED} !important; }}
[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-baseweb="menu"] li,
[data-baseweb="menu"] li span,
[data-baseweb="option"] {{
    background-color: {INPUT_BG} !important;
    color: {TEXT} !important;
}}
[data-baseweb="option"]:hover {{
    background-color: {PRIMARY_SOFT} !important;
}}

/* ── Time input ── */
.stTimeInput > div > div > input,
input[type="time"] {{
    background-color: {INPUT_BG} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.stTimeInput label {{ color: {TEXT_MUTED} !important; }}

/* ── Slider ── */
.stSlider > div > div > div > div {{
    background-color: {PRIMARY} !important;
}}
.stSlider label {{ color: {TEXT_MUTED} !important; }}
.stSlider span {{ color: {TEXT} !important; }}

/* ── Chat input ── */
.stChatInput,
.stChatInput > div,
[data-testid="stChatInput"],
[data-testid="stChatInputContainer"] {{
    background-color: {INPUT_BG} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 14px !important;
}}
.stChatInput textarea,
[data-testid="stChatInputTextArea"] {{
    background-color: {INPUT_BG} !important;
    color: {TEXT} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    caret-color: {PRIMARY} !important;
}}
.stChatInput textarea:focus {{
    border-color: {PRIMARY} !important;
    box-shadow: 0 0 0 3px {"rgba(77,142,255,0.2)" if dark else "rgba(30,111,255,0.15)"} !important;
}}
.stChatInput button,
[data-testid="stChatInputSubmitButton"] {{
    background-color: {PRIMARY} !important;
    color: #fff !important;
    border-radius: 10px !important;
}}

/* ── Buttons ── */
.stButton > button {{
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    border: 1px solid {BORDER} !important;
    background-color: {SURFACE} !important;
    color: {TEXT} !important;
    transition: all 0.15s !important;
    padding: 8px 14px !important;
    width: 100% !important;
    text-align: left !important;
}}
.stButton > button:hover {{
    background-color: {PRIMARY_SOFT} !important;
    border-color: {PRIMARY} !important;
    color: {PRIMARY} !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
}}

/* ── Download button ── */
.stDownloadButton > button {{
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 10px !important;
    border: 1px solid {BORDER} !important;
    background-color: {SURFACE} !important;
    color: {TEXT} !important;
    width: 100% !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
.stFileUploader,
.stFileUploader > div {{
    background-color: {SURFACE2} !important;
    border: 1.5px dashed {BORDER} !important;
    border-radius: 12px !important;
    color: {TEXT} !important;
}}
.stFileUploader label,
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] p {{
    color: {TEXT_MUTED} !important;
}}
[data-testid="stFileUploadDropzone"] {{
    background-color: {SURFACE2} !important;
    border-color: {BORDER} !important;
}}

/* ── Expander ── */
.stExpander,
.stExpander > div,
[data-testid="stExpander"] {{
    background-color: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
}}
.stExpander summary,
.stExpander summary span,
[data-testid="stExpander"] summary {{
    color: {TEXT} !important;
    background-color: {SURFACE} !important;
}}
.stExpander [data-testid="stExpanderDetails"] {{
    background-color: {SURFACE} !important;
}}

/* ── Alerts: success / warning / info / error ── */
.stSuccess, .stSuccess > div,
[data-testid="stNotification"][data-baseweb="notification"][kind="positive"] {{
    background-color: {"#162A1A" if dark else "#F0FFF4"} !important;
    color: {"#4ADE80" if dark else "#166534"} !important;
    border: 1px solid {"#2D5A3A" if dark else "#BBF7D0"} !important;
    border-radius: 10px !important;
}}
.stWarning, .stWarning > div {{
    background-color: {"#2A2015" if dark else "#FFFBEB"} !important;
    color: {"#FCD34D" if dark else "#92400E"} !important;
    border: 1px solid {"#5C4A00" if dark else "#FDE68A"} !important;
    border-radius: 10px !important;
}}
.stInfo, .stInfo > div {{
    background-color: {"#0F1F35" if dark else "#EFF6FF"} !important;
    color: {"#93C5FD" if dark else "#1E40AF"} !important;
    border: 1px solid {"#1E3A5F" if dark else "#BFDBFE"} !important;
    border-radius: 10px !important;
}}
.stError, .stError > div {{
    background-color: {"#2A0F0F" if dark else "#FEF2F2"} !important;
    color: {"#FCA5A5" if dark else "#991B1B"} !important;
    border: 1px solid {"#5C1A1A" if dark else "#FECACA"} !important;
    border-radius: 10px !important;
}}

/* ── Spinner ── */
.stSpinner > div {{
    border-top-color: {PRIMARY} !important;
}}

/* ── Caption ── */
.stCaption, .stCaption p {{
    color: {TEXT_MUTED} !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 3px; }}

/* ── TOP NAVIGATION BAR ── */
.top-nav-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 24px;
    background-color: {NAV_BG};
    border-bottom: 1px solid {NAV_BORDER};
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: {SHADOW};
    flex-wrap: wrap;
    gap: 10px;
}}
.top-nav-brand {{
    font-family: 'Sora', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: {TEXT};
    display: flex;
    align-items: center;
    gap: 10px;
    white-space: nowrap;
}}
.top-nav-pills {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: {SURFACE2};
    border-radius: 12px;
    padding: 4px;
    border: 1px solid {BORDER};
}}
.top-nav-pill {{
    padding: 7px 18px;
    border-radius: 9px;
    font-size: 13px;
    font-weight: 600;
    color: {TEXT_MUTED};
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s;
}}
.top-nav-pill.active {{
    background: {PRIMARY};
    color: #fff;
    box-shadow: 0 2px 8px rgba(30,111,255,0.35);
}}
.top-nav-right {{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}}
.top-nav-badge {{
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    background: {PRIMARY_SOFT};
    color: {PRIMARY};
    white-space: nowrap;
}}
.top-nav-tagline {{
    font-size: 12px;
    color: {TEXT_MUTED};
    background: {SURFACE2};
    border: 1px solid {BORDER};
    padding: 4px 12px;
    border-radius: 20px;
    white-space: nowrap;
}}

/* ── Sidebar logo ── */
.sb-logo {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 18px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 16px;
}}
.sb-logo-icon {{
    width: 44px;
    height: 44px;
    background: {PRIMARY};
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}}
.sb-logo-text {{
    font-family: 'Sora', sans-serif;
    font-size: 19px;
    font-weight: 700;
    color: {TEXT};
}}
.sb-logo-sub {{
    font-size: 11px;
    color: {TEXT_MUTED};
    margin-top: 2px;
}}

/* ── Section label ── */
.sb-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {TEXT_MUTED} !important;
    margin: 16px 0 8px;
    display: block;
}}

/* ── Report badge ── */
.report-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {PRIMARY_SOFT};
    color: {PRIMARY};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 8px;
}}
.report-badge.inactive {{
    background: {SURFACE2};
    color: {TEXT_MUTED};
}}

/* ── Message bubbles ── */
.msg-row {{
    display: flex;
    align-items: flex-end;
    gap: 10px;
    animation: fadeUp 0.25s ease;
    margin-bottom: 4px;
}}
.msg-row.user {{ flex-direction: row-reverse; }}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.avatar {{
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
    background: {PRIMARY_SOFT};
}}
.avatar.user {{ background: {PRIMARY}; }}
.bubble {{
    max-width: 70%;
    padding: 13px 17px;
    border-radius: 18px;
    font-size: 14px;
    line-height: 1.65;
    box-shadow: {SHADOW};
}}
.bubble.bot {{
    background: {BOT_BUBBLE};
    border-bottom-left-radius: 4px;
    color: {TEXT};
    border: 1px solid {BORDER};
}}
.bubble.user {{
    background: linear-gradient(135deg, {PRIMARY} 0%, {"#1A3AB5" if dark else "#0A4FD6"} 100%);
    border-bottom-right-radius: 4px;
    color: #fff;
}}
.bubble.bot p, .bubble.bot span, .bubble.bot li {{ color: {TEXT} !important; }}
.bubble.user p, .bubble.user span {{ color: #fff !important; }}
.msg-meta {{
    font-size: 10px;
    color: {TEXT_MUTED};
    margin-top: 3px;
    padding: 0 44px;
}}
.msg-meta.user {{ text-align: right; }}

/* ── Suggestion chips ── */
.sug-label {{
    font-size: 11px;
    font-weight: 700;
    color: {TEXT_MUTED};
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 12px;
    display: block;
}}

/* ── Disclaimer box ── */
.disclaimer-box {{
    background: {DISC_BG};
    border: 1px solid {DISC_BORDER};
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 12px;
    color: {DISC_TEXT};
    margin: 12px 0;
}}
.disclaimer-box strong {{ color: {DISC_TEXT} !important; }}

/* ── Card ── */
.card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 12px;
    box-shadow: {SHADOW};
}}
.card-title {{
    font-family: 'Sora', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: {TEXT};
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}}

/* ── Reminder pill ── */
.reminder-pill {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: {SURFACE2};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
}}
.reminder-name {{ font-weight: 600; font-size: 14px; color: {TEXT}; }}
.reminder-meta {{ font-size: 12px; color: {TEXT_MUTED}; }}
.reminder-time {{
    background: {PRIMARY_SOFT};
    color: {PRIMARY};
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 700;
}}

/* ── Topbar (legacy, now replaced by top-nav-bar) ── */
.topbar {{
    display: none;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  GROQ API CALL
# ─────────────────────────────────────────────
def call_api(question: str, report_text: str, language: str, system_override: str = None) -> str:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise ValueError("API key not configured. Add GROQ_API_KEY to Streamlit Secrets.")

    lang_name = language.split("(")[-1].strip().rstrip(")") if "(" in language else language

    if system_override:
        system_prompt = system_override
    else:
        system_prompt = f"""You are 'CareBuddy', a specialized AI health assistant.
LANGUAGE: Always respond in {lang_name}.
RULES:
1. ONLY answer questions about: medical conditions, symptoms, treatments, anatomy, physiology, nutrition, mental health, wellness, and interpretation of medical reports.
2. If a report is provided, use it as primary context.
3. Reject non-health questions politely in the same language.
4. NEVER diagnose or prescribe. Suggest seeing a doctor for serious symptoms.
5. Keep responses clear, structured, and under 350 words.
6. End EVERY response with a one-line disclaimer that this is educational only.
"""
    payload = {
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 700,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Medical Report:\n{report_text}\n\nQuestion:\n{question}"
                    if report_text else question
                ),
            },
        ],
    }
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as exc:
        err_body = {}
        try:
            err_body = resp.json()
        except Exception:
            pass
        err_msg = err_body.get("error", {}).get("message", str(exc))
        raise ValueError(f"{t('error_api')}: {err_msg}")
    except requests.exceptions.Timeout:
        raise ValueError("Request timed out. Please try again.")
    except Exception as exc:
        raise ValueError(f"{t('error_generic')}: {exc}")


# ─────────────────────────────────────────────
#  TEXT EXTRACTION
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def extract_pdf(file_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n".join(pages)

def compress_image(file_bytes: bytes, max_kb: int = 900) -> bytes:
    """Compress image to stay under OCR.space's 1024 KB limit."""
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    quality = 85
    while True:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_kb or quality < 20:
            return buffer.getvalue()
        # Also downscale if still too large after quality reduction
        if quality <= 40:
            w, h = img.size
            img = img.resize((int(w * 0.75), int(h * 0.75)), Image.LANCZOS)
        quality -= 10

def extract_image(file_bytes: bytes) -> str:
    try:
        # Compress image if over 900 KB
        if len(file_bytes) > 900 * 1024:
            file_bytes = compress_image(file_bytes)

        b64_image = base64.b64encode(file_bytes).decode("utf-8")
        payload = {
            "base64Image": f"data:image/jpeg;base64,{b64_image}",
            "apikey": "K84494792088957",
            "language": "eng",
            "isOverlayRequired": False,
            "detectOrientation": True,
            "scale": True,
            "OCREngine": 2,
        }
        resp = requests.post(
            "https://api.ocr.space/parse/image",
            data=payload,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("IsErroredOnProcessing"):
            error_msg = result.get("ErrorMessage", ["Unknown OCR error"])[0]
            return f"[OCR failed: {error_msg}]"
        parsed_results = result.get("ParsedResults", [])
        if not parsed_results:
            return "[No text found in image]"
        return "\n".join(r.get("ParsedText", "") for r in parsed_results).strip()
    except requests.exceptions.Timeout:
        return "[OCR request timed out. Please try again.]"
    except Exception as exc:
        return f"[Image extraction failed: {exc}]"


# ─────────────────────────────────────────────
#  CHAT HANDLER
# ─────────────────────────────────────────────
def handle_chat(prompt: str):
    prompt = prompt.strip()
    if not prompt:
        return
    ts = datetime.datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": prompt, "ts": ts})
    searches = list(st.session_state.recent_searches)
    if prompt not in searches:
        st.session_state.recent_searches.appendleft(prompt)
    with st.spinner(t("thinking")):
        try:
            reply = call_api(prompt, st.session_state.report_text, st.session_state.language)
        except ValueError as exc:
            reply = f"❌ {exc}"
    st.session_state.messages.append({
        "role": "bot",
        "content": reply,
        "ts": datetime.datetime.now().strftime("%H:%M"),
    })
    st.rerun()


# ─────────────────────────────────────────────
#  RENDER MESSAGES
# ─────────────────────────────────────────────
def render_messages():
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg.get("content", "")
        ts = msg.get("ts", "")
        is_user = role == "user"
        if is_user:
            st.markdown(f"""
<div class="msg-row user">
  <div class="avatar user">👤</div>
  <div class="bubble user">{content}</div>
</div>
<div class="msg-meta user">{t('you')} · {ts}</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div class="msg-row bot">
  <div class="avatar">🩺</div>
  <div class="bubble bot">{content}</div>
</div>
<div class="msg-meta">{t('carebuddy')} · {ts}</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SYMPTOM CHECKER TAB
# ─────────────────────────────────────────────
def render_symptom_checker():
    st.markdown(f'<div class="card"><div class="card-title">{t("symptom_checker")}</div>', unsafe_allow_html=True)
    symptoms = st.text_input(
        t("symptom_input"),
        placeholder=t("symptom_placeholder"),
        key="symptom_input_field",
    )
    col1, col2 = st.columns(2)
    with col1:
        duration = st.selectbox(t("symptom_duration"), t("duration_options"), key="sym_duration")
    with col2:
        severity = st.slider(t("symptom_severity"), 1, 10, 3, key="sym_severity")

    pct = int(severity * 10)
    sev_color = "#00C9A7" if severity <= 3 else "#FFC107" if severity <= 6 else "#FF5C5C"
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;margin:4px 0 16px;">
  <div style="flex:1;height:8px;border-radius:4px;background:linear-gradient(to right,#00C9A7 0%,#FFC107 50%,#FF5C5C 100%);position:relative;">
    <div style="position:absolute;left:0;top:0;height:100%;width:{pct}%;border-radius:4px;background:transparent;border-right:2px solid {sev_color};"></div>
  </div>
  <span style="font-size:13px;font-weight:700;color:{sev_color};">{severity}/10</span>
</div>
""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button(t("analyze_symptoms"), use_container_width=True, key="sym_btn"):
        if not symptoms.strip():
            st.warning("Please enter at least one symptom.")
            return
        lang_name = st.session_state.language.split("(")[-1].strip().rstrip(")") if "(" in st.session_state.language else st.session_state.language
        system_prompt = f"""You are CareBuddy, a medical AI assistant. Respond in {lang_name}.
Analyze the given symptoms and provide:
1. **Possible Conditions** – list 2–4 plausible causes (NOT a diagnosis)
2. **Recommended Actions** – what the user should do
3. **Warning Signs** – symptoms that require immediate emergency care
Keep it concise, clear, and structured. End with a disclaimer."""
        query = f"Symptoms: {symptoms}\nDuration: {duration}\nSeverity: {severity}/10"
        with st.spinner(t("thinking")):
            try:
                result = call_api(query, "", st.session_state.language, system_override=system_prompt)
                st.session_state.symptom_result = result
            except ValueError as exc:
                st.error(str(exc))

    if st.session_state.symptom_result:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">🩺 {t("symptom_result")}</div>', unsafe_allow_html=True)
        st.markdown(st.session_state.symptom_result)
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MEDICATION REMINDERS TAB
# ─────────────────────────────────────────────
def render_reminders():
    st.markdown(f'<div class="card"><div class="card-title">{t("med_reminder")}</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        med_name = st.text_input(t("med_name"), placeholder="e.g. Metformin", key="med_name_input")
    with col2:
        med_dose = st.text_input(t("med_dose"), placeholder="e.g. 500mg", key="med_dose_input")
    with col3:
        med_time = st.time_input(t("med_time"), value=datetime.time(8, 0), key="med_time_input")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button(t("add_reminder"), use_container_width=True, key="add_rem_btn"):
        if med_name.strip():
            st.session_state.reminders.append({
                "id": len(st.session_state.reminders),
                "name": med_name.strip(),
                "dose": med_dose.strip() or "—",
                "time": med_time.strftime("%H:%M"),
            })
            st.success(f"✅ Reminder added for {med_name}!")
            st.rerun()
        else:
            st.warning("Please enter a medication name.")

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    st.markdown(f'<span class="sb-label">{t("reminders_today")}</span>', unsafe_allow_html=True)

    if not st.session_state.reminders:
        st.info(t("no_reminders"))
    else:
        sorted_reminders = sorted(st.session_state.reminders, key=lambda x: x["time"])
        to_delete = None
        for rem in sorted_reminders:
            is_upcoming = rem["time"] >= current_time
            status_icon = "🔔" if is_upcoming else "✅"
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"""
<div class="reminder-pill">
  <div style="display:flex;flex-direction:column;gap:2px;">
    <div class="reminder-name">{status_icon} {rem['name']}</div>
    <div class="reminder-meta">{rem['dose']}</div>
  </div>
  <div class="reminder-time">⏰ {rem['time']}</div>
</div>
""", unsafe_allow_html=True)
            with col_b:
                if st.button(t("delete"), key=f"del_{rem['id']}", help="Delete reminder"):
                    to_delete = rem["id"]
        if to_delete is not None:
            st.session_state.reminders = [r for r in st.session_state.reminders if r["id"] != to_delete]
            st.rerun()


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
<div class="sb-logo">
  <div class="sb-logo-icon">🩺</div>
  <div>
    <div class="sb-logo-text">CareBuddy</div>
    <div class="sb-logo-sub">AI Health Assistant</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Language
    st.markdown(f'<span class="sb-label">{t("sidebar_language")}</span>', unsafe_allow_html=True)
    prev_lang = st.session_state.language
    selected_lang = st.selectbox(
        label="language_select",
        options=list(TRANSLATIONS.keys()),
        index=list(TRANSLATIONS.keys()).index(st.session_state.language),
        label_visibility="collapsed",
        key="lang_select",
    )
    if selected_lang != prev_lang:
        st.session_state.language = selected_lang
        st.session_state.messages = [
            {"role": "bot", "content": TRANSLATIONS[selected_lang]["welcome_msg"],
             "ts": datetime.datetime.now().strftime("%H:%M")}
        ]
        st.rerun()

    # Dark mode toggle
    st.markdown('<span class="sb-label">Theme</span>', unsafe_allow_html=True)
    dm_label = t("light_mode") if dark else t("dark_mode")
    if st.button(dm_label, use_container_width=True, key="dark_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    # Actions
    st.markdown(f'<span class="sb-label">{t("sidebar_actions")}</span>', unsafe_allow_html=True)
    if st.button(t("clear_chat"), use_container_width=True, key="clear_btn"):
        st.session_state.messages = [
            {"role": "bot", "content": t("chat_cleared"), "ts": datetime.datetime.now().strftime("%H:%M")}
        ]
        st.session_state.report_text = ""
        st.session_state.report_name = ""
        st.session_state.recent_searches.clear()
        st.session_state.symptom_result = None
        st.rerun()

    if st.session_state.messages:
        chat_str = "\n\n".join(
            f"[{msg.get('ts','')}] {msg['role'].upper()}:\n{msg['content']}"
            for msg in st.session_state.messages
        )
        ts_stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        st.download_button(
            label=t("download_chat"),
            data=chat_str,
            file_name=f"CareBuddy_Chat_{ts_stamp}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_btn",
        )

    # Report upload
    st.markdown(f'<span class="sb-label">{t("upload_header")}</span>', unsafe_allow_html=True)
    if st.session_state.report_text:
        st.markdown(
            f'<div class="report-badge">📄 {st.session_state.report_name or "Report"}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="report-badge inactive">{t("no_report_badge")}</div>',
            unsafe_allow_html=True,
        )

    uploaded = st.file_uploader(
        label=t("upload_help"),
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed",
        key="file_uploader",
    )
    if uploaded:
        file_bytes = uploaded.read()
        with st.spinner(t("extraction")):
            if uploaded.type == "application/pdf":
                text = extract_pdf(file_bytes)
            else:
                text = extract_image(file_bytes)
        if text.strip():
            st.session_state.report_text = text
            st.session_state.report_name = uploaded.name
            st.success(t("upload_success"))
            with st.expander(t("view_text")):
                st.text_area("", text, height=180, key="extracted_text")
        else:
            st.warning(t("upload_empty"))

    # Recent searches
    if st.session_state.active_tab == "chat":
        st.markdown(f'<span class="sb-label">{t("recent_header")}</span>', unsafe_allow_html=True)
        if not st.session_state.recent_searches:
            st.caption(t("recent_empty"))
        else:
            for idx, search in enumerate(list(st.session_state.recent_searches)):
                label = search[:40] + "…" if len(search) > 40 else search
                if st.button(label, key=f"recent_{idx}", use_container_width=True):
                    handle_chat(search)

    # Disclaimer
    st.markdown(
        f'<div class="disclaimer-box"><strong>{t("disclaimer_label")}</strong><br>{t("disclaimer_text")}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
#  TOP NAV BAR — single, functional, Streamlit buttons only
# ─────────────────────────────────────────────
active_tab = st.session_state.active_tab
report_pill = (
    f'<span style="font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;'
    f'background:{PRIMARY_SOFT};color:{PRIMARY};margin-left:8px;">📄 {st.session_state.report_name}</span>'
    if st.session_state.report_text else ""
)

# Brand header row
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:14px 4px 4px 4px;margin-bottom:2px;">
  <div style="display:flex;align-items:center;gap:8px;">
    <span style="font-family:'Sora',sans-serif;font-size:22px;font-weight:800;color:{TEXT};">
      🩺 CareBuddy
    </span>
    {report_pill}
  </div>
  <span style="font-size:12px;color:{TEXT_MUTED};background:{SURFACE2};
               border:1px solid {BORDER};padding:4px 12px;border-radius:20px;">
    {t('app_tagline')}
  </span>
</div>
""", unsafe_allow_html=True)

# Navigation buttons row — balanced columns, no wasted space
nav_c1, nav_c2, nav_c3 = st.columns(3)
with nav_c1:
    if st.button(t("nav_chat"), key="top_nav_chat", use_container_width=True,
                 type="primary" if active_tab == "chat" else "secondary"):
        st.session_state.active_tab = "chat"
        st.rerun()
with nav_c2:
    if st.button(t("nav_symptoms"), key="top_nav_sym", use_container_width=True,
                 type="primary" if active_tab == "symptoms" else "secondary"):
        st.session_state.active_tab = "symptoms"
        st.rerun()
with nav_c3:
    if st.button(t("nav_reminders"), key="top_nav_rem", use_container_width=True,
                 type="primary" if active_tab == "reminders" else "secondary"):
        st.session_state.active_tab = "reminders"
        st.rerun()


# ─────────────────────────────────────────────
#  MAIN CONTENT — Tab routing
# ─────────────────────────────────────────────
active_tab = st.session_state.active_tab  # re-read after potential rerun
if active_tab == "chat":
    render_messages()
    if len(st.session_state.messages) <= 2:
        st.markdown(f'<span class="sug-label">{t("suggestions_label")}</span>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, s in enumerate(t("suggestions")):
            with cols[i % 2]:
                if st.button(s, key=f"sug_{i}"):
                    handle_chat(s)

    if prompt := st.chat_input(t("input_placeholder")):
        handle_chat(prompt)

elif active_tab == "symptoms":
    render_symptom_checker()

elif active_tab == "reminders":
    render_reminders()