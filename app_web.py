import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import io
import datetime as dt

# ===========================
#  CONFIG
# ===========================
st.set_page_config(
    page_title="Maintenance Trident-OGX",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================
#  THEME CSS GLOBAL
# ===========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Source+Sans+3:wght@300;400;600&display=swap');

:root {
    --bg-primary:   #f0f2f5;
    --bg-secondary: #e4e7ec;
    --bg-card:      #ffffff;
    --accent:       #f97316;
    --accent-dim:   #fed7aa;
    --text-main:    #1a2332;
    --text-muted:   #64748b;
    --border:       #d1d5db;
    --success:      #16a34a;
    --danger:       #dc2626;
    --warning:      #ca8a04;
    --info:         #2563eb;
    --shadow:       0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-md:    0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05);
}

[data-testid="stAppViewContainer"] {
    background: var(--bg-primary);
    color: var(--text-main);
    font-family: 'Source Sans 3', sans-serif;
}
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--border);
    box-shadow: var(--shadow-md);
}
h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 1px;
    color: var(--text-main) !important;
}
.stButton > button {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-main);
    border-radius: 6px;
    padding: 0.5rem 1.2rem;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.2s;
    box-shadow: var(--shadow);
}
.stButton > button:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: rgba(249,115,22,0.06);
    box-shadow: var(--shadow-md);
}
[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    box-shadow: var(--shadow);
}
[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
[data-testid="stMetricValue"] {
    color: var(--text-main) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}
[data-testid="stRadio"] label {
    color: var(--text-muted) !important;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    letter-spacing: 0.5px;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px;
    box-shadow: var(--shadow);
}
.stSelectbox label, .stMultiSelect label, .stDateInput label {
    color: var(--text-muted) !important;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
hr { border-color: var(--border) !important; }
.module-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
    height: 170px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow);
}
.module-card:hover {
    border-color: var(--accent);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(249,115,22,0.12);
}
.module-card-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.module-card-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-main);
    letter-spacing: 1px;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.badge-red    { background: rgba(220,38,38,0.1);  color: #dc2626; border: 1px solid #dc2626; }
.badge-orange { background: rgba(249,115,22,0.1); color: #f97316; border: 1px solid #f97316; }
.badge-yellow { background: rgba(202,138,4,0.1);  color: #ca8a04; border: 1px solid #ca8a04; }
.badge-green  { background: rgba(22,163,74,0.1);  color: #16a34a; border: 1px solid #16a34a; }
.page-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 0 1.5rem;
    border-bottom: 2px solid var(--border);
    margin-bottom: 1.5rem;
}
.page-header h1 { margin: 0 !important; font-size: 1.8rem !important; }
.page-header .accent-line {
    width: 4px; height: 32px;
    background: var(--accent); border-radius: 4px;
}

/* ===== ANIMATION APPARITION LOGIN ===== */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* CECI EST LE POINT IMPORTANT */
.login-logo-box {
    width: 450px;
    height: 100px;
    margin: 0 auto 1.2rem auto;
    border-radius: 18px;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    overflow: hidden;

    /*  AJOUT ANIMATION SUBTILE */
    animation: logoPulse 3s ease-in-out infinite;
}

/* ===== ANIMATION LOGO (PULSE DOUX) ===== */
@keyframes logoPulse {
    0% {
        transform: scale(1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
    50% {
        transform: scale(1.03);
        box-shadow: 0 15px 40px rgba(0,0,0,0.18);
    }
    100% {
        transform: scale(1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
}

/* contrôle du logo */
.login-logo {
    max-width: 180%;
    max-height: 400%;
    object-fit: contain;

    /* petite amélioration visuelle */
    transition: transform 0.3s ease;
}

/* effet hover discret (pro) */
.login-logo:hover {
    transform: scale(1.05);
}

/* fallback texte */
.login-logo-placeholder {
    width: 160px;
    height: 64px;
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    letter-spacing: 2px;
}
.login-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.6rem; font-weight: 700;
    text-align: center; letter-spacing: 2px;
    color: var(--accent) !important; margin-bottom: 0.3rem;
}
.login-sub {
    text-align: center; font-size: 0.85rem;
    color: var(--text-muted); margin-bottom: 2rem; letter-spacing: 1px;
}
.kpi-icon-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    box-shadow: var(--shadow);
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 0.5rem;
}
.kpi-icon-wrap {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.kpi-icon-blue   { background: rgba(37,99,235,0.1); }
.kpi-icon-orange { background: rgba(249,115,22,0.1); }
.kpi-icon-red    { background: rgba(220,38,38,0.1); }
.kpi-icon-green  { background: rgba(22,163,74,0.1); }
.kpi-icon-yellow { background: rgba(202,138,4,0.1); }
.kpi-icon-purple { background: rgba(124,58,237,0.1); }
.kpi-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); margin: 0; }
.kpi-value { font-family: 'Rajdhani', sans-serif; font-size: 1.8rem; font-weight: 700; color: var(--text-main); margin: 0; line-height: 1.1; }
.kpi-delta { font-size: 0.75rem; color: var(--text-muted); margin: 0; }
.section-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stTextArea"] textarea {
    background: #f8fafc !important;
    border-color: var(--border) !important;
    color: var(--text-main) !important;
}
</style>
""", unsafe_allow_html=True)

# ===========================
#  SVG ICONS
# ===========================
ICONS = {
    "total":      '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="m9 12 2 2 4-4"/></svg>',
    "panne":      '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "hs":         '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>',
    "dispo":      '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "equip":      '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>',
    "taux":       '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "planning":   '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "realise":    '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "ecart":      '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ca8a04" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "correctif":  '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
    "mtbf":       '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="6" height="6" rx="1"/><rect x="16" y="2" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><path d="M5 8v3a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8"/><path d="M19 16v-3"/></svg>',
    "urgent":     '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "jours":      '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "charge":     '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "crit_rouge": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "crit_elev":  '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3z"/></svg>',
    "crit_mod":   '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ca8a04" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "crit_faib":  '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "op_total":   '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>',
    "op_panne":   '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/></svg>',
    "op_hs":      '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>',
    "op_dispo":   '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
}

def kpi_card(icon_key, label, value, color_class="kpi-icon-blue", delta=None):
    delta_html = f'<p class="kpi-delta">{delta}</p>' if delta else ""
    return f"""
    <div class="kpi-icon-card">
        <div class="kpi-icon-wrap {color_class}">{ICONS.get(icon_key,'')}</div>
        <div>
            <p class="kpi-label">{label}</p>
            <p class="kpi-value">{value}</p>
            {delta_html}
        </div>
    </div>
    """

# ===========================
#  SESSION STATE
# ===========================
for key, val in [("login", False), ("module", "home"), ("equipements_db", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ===========================
#  LOGIN
# ===========================
USERS = {
    "admin":     ("Trident@26", "Administrateur"),
    "florent.nkouka@trident-ogx.com": ("Dir@2026",   "Direction"),
    "tech":      ("Tech@2024",  "Technicien"),
}

import os
import base64

def get_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

if not st.session_state["login"]:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    # ===== LOGO DANS LE CARRÉ =====
    if os.path.exists("logo.png"):
        logo_base64 = get_base64_image("logo.png")

        st.markdown(f"""
        <div class="login-logo-box">
            <img src="data:image/png;base64,{logo_base64}" class="login-logo">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="login-logo-box">
            <div class="login-logo-placeholder">⚙ APT</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="login-title">⚙ TRIDENT-OGX</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">SYSTÈME DE MAINTENANCE INDUSTRIELLE</div>', unsafe_allow_html=True)

    user     = st.text_input("Identifiant", placeholder="Votre identifiant")
    password = st.text_input("Mot de passe", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("CONNEXION", use_container_width=True):
        if user in USERS and password == USERS[user][0]:
            st.session_state["login"]    = True
            st.session_state["username"] = USERS[user][1]
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ===========================
#  LOAD DATA
# ===========================
@st.cache_data
def load_journal():
    try:
        df = pd.read_excel("journal.xlsx")
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        np.random.seed(42)
        # Colonne nommée "Tag" comme dans le vrai fichier journal
        tags = [f"TAG-{i:03d}" for i in range(1, 21)]
        equipements = ["Pompe A", "Compresseur B", "Turbine C", "Chaudière D", "Moteur E",
                       "Vanne F", "Échangeur G", "Filtre H", "Convoyeur I", "Réducteur J"]
        types_ops   = ["Correctif", "Préventif", "Signalement", "Surveillance", "Travaux"]
        specialites = ["Mécanique", "Électrique", "Instrumentation", "Hydraulique"]
        statuts     = ["Opérationnel", "HS", "En cours"]
        n = 300
        dates = pd.date_range("2024-01-01", "2025-05-01", periods=n)
        return pd.DataFrame({
            "Date":                 dates,
            "Tag":                  np.random.choice(tags, n),   # "Tag" = journal
            "Equipement":           np.random.choice(equipements, n),
            "Type d'opération":     np.random.choice(types_ops, n),
            "Spécialité":           np.random.choice(specialites, n),
            "Statut opérationnel":  np.random.choice(statuts, n, p=[0.7, 0.15, 0.15]),
            "Description":          [f"Opération de maintenance #{i}" for i in range(n)],
            "Durée (h)":            np.random.uniform(0.5, 8, n).round(1),
        })

@st.cache_data
def load_planning():
    try:
        df = pd.read_excel("planning_annuel.xlsx")
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        np.random.seed(7)
        n = 150
        dates_debut = pd.date_range("2025-01-01", "2025-12-01", periods=n)
        return pd.DataFrame({
            "Semaine":    np.random.randint(1, 53, n),
            "Début":      dates_debut,
            "Fin":        dates_debut + pd.to_timedelta(np.random.randint(1, 7, n), unit="D"),
            "Equipement": np.random.choice(["Pompe A","Compresseur B","Turbine C","Moteur E"], n),
            "TAG":        [f"TAG-{i:03d}" for i in np.random.randint(1, 21, n)],  # "TAG" = planning
            "Description":[f"Tâche préventive #{i}" for i in range(n)],
            "Spécialité": np.random.choice(["Mécanique","Électrique","Instrumentation"], n),
            "Site":       np.random.choice(["Unité A","Unité B","Unité C"], n),
            "Zone":       np.random.choice(["Zone Nord","Zone Sud","Zone Est"], n),
            "Criticité":  np.random.choice(["Faible","Modérée","Élevée","Critique"], n, p=[0.3,0.4,0.2,0.1]),
            "Fabricant":  np.random.choice(["Grundfos","Siemens","ABB","Schneider"], n),
        })

df = load_journal()
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# ── Normalisation Tag/TAG dans le journal ──
# Le journal utilise "Tag", on garde tel quel mais on crée un alias pour les filtres
COL_TAG_JOURNAL  = "Tag"   # colonne réelle dans journal.xlsx
COL_TAG_PLANNING = "TAG"   # colonne réelle dans planning_annuel.xlsx

def categoriser(x):
    if pd.isna(x): return "Autre"
    x = str(x).lower()
    if "correctif"   in x: return "Correctif"
    if "préventif"   in x: return "Préventif"
    if "signalement" in x: return "Signalement"
    if "surveil"     in x: return "Surveillance"
    if "travaux"     in x: return "Travaux"
    return "Autre"

df["Categorie"] = df["Type d'opération"].apply(categoriser)

# ===========================
#  HELPERS
# ===========================
def page_header(icon, title):
    st.markdown(f"""
    <div class="page-header">
        <div class="accent-line"></div>
        <h1>{icon} {title}</h1>
    </div>
    """, unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(248,250,252,0.5)",
    font=dict(color="#1a2332", family="Source Sans 3"),
    margin=dict(t=30, b=10, l=10, r=10),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

# ===========================
#  HOME HUB
# ===========================
if st.session_state["module"] == "home":
    page_header("⚙", "MAINTENANCE SYSTÈME TRIDENT-OGX")

    user_label = st.session_state.get("username", "Utilisateur")
    st.markdown(f"<p style='color:#64748b;margin-bottom:2rem;'>Bienvenue, <b style='color:#f97316'>{user_label}</b> — {datetime.now().strftime('%A %d %B %Y, %H:%M')}</p>", unsafe_allow_html=True)

    # ── 5 modules : 3 en haut, 2 en bas ──
    modules_row1 = [
        ("equipements",    "🔧", "Suivi des équipements"),
        ("planning",       "📅", "Planning maintenance"),
        ("direction",      "📊", "Dashboard Direction"),
    ]
    modules_row2 = [
        ("gestion_equip",   "🗂️", "Gestion équipements"),
        ("suivi_execution", "📈", "Suivi d'exécution"),
    ]

    col1, col2, col3 = st.columns(3, gap="large")
    for i, (mod, icon, label) in enumerate(modules_row1):
        with [col1, col2, col3][i]:
            st.markdown(f'<div class="module-card"><div class="module-card-icon">{icon}</div><div class="module-card-title">{label}</div></div>', unsafe_allow_html=True)
            if st.button("Accéder →", key=mod):
                st.session_state["module"] = mod
                st.rerun()

    st.markdown("")
    col4, col5, _ = st.columns(3, gap="large")
    for col, (mod, icon, label) in zip([col4, col5], modules_row2):
        with col:
            st.markdown(f'<div class="module-card"><div class="module-card-icon">{icon}</div><div class="module-card-title">{label}</div></div>', unsafe_allow_html=True)
            if st.button("Accéder →", key=mod):
                st.session_state["module"] = mod
                st.rerun()

    # Résumé rapide
    st.markdown("---")
    st.markdown("#### Résumé global")
    total_h  = len(df)
    pannes_h = len(df[df["Categorie"] == "Correctif"])
    hs_h     = len(df[df["Statut opérationnel"] == "HS"]) if "Statut opérationnel" in df.columns else 0
    dispo_h  = round((total_h - hs_h) / total_h * 100, 1) if total_h else 0
    equips_h = df["Equipement"].nunique() if "Equipement" in df.columns else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(kpi_card("op_total", "Total interventions", total_h,  "kpi-icon-blue"),   unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("op_panne", "Pannes",              pannes_h, "kpi-icon-red"),    unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("op_hs",    "Équipements HS",      hs_h,     "kpi-icon-red"),    unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("op_dispo", "Disponibilité",       f"{dispo_h}%", "kpi-icon-green"), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("equip",    "Équipements",         equips_h, "kpi-icon-orange"), unsafe_allow_html=True)

    st.stop()

# ===========================
#  SIDEBAR COMMUNE
# ===========================
def back_button():
    if st.sidebar.button("⬅  Retour accueil"):
        st.session_state["module"] = "home"
        st.rerun()

# ===========================
#  MODULE ÉQUIPEMENTS
# ===========================
if st.session_state["module"] == "equipements":
    back_button()
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙ Navigation")

    menu = st.sidebar.radio("", [
        "Dashboard",
        "Journal",
        "Équipes",
        "Criticité",
        "Prédictif",
        "Rapports",
    ])

    # ── FILTRES — utilise "Tag" (journal) ──
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filtres")
    date_range = st.sidebar.date_input("Période", [])
    equipement = st.sidebar.multiselect("Équipement", sorted(df["Equipement"].dropna().unique()))

    # Tag dans le journal s'appelle "Tag"
    tag_col = COL_TAG_JOURNAL  # "Tag"
    tag_vals = sorted(df[tag_col].dropna().unique(), key=lambda x: str(x)) if tag_col in df.columns else []
    tag_sel  = st.sidebar.multiselect("Tag", tag_vals)

    specialite = st.sidebar.multiselect("Spécialité", sorted(df["Spécialité"].dropna().unique()) if "Spécialité" in df.columns else [])

    df_f = df.copy()
    if len(date_range) == 2:
        df_f = df_f[(df_f["Date"] >= pd.to_datetime(date_range[0])) & (df_f["Date"] <= pd.to_datetime(date_range[1]))]
    if equipement: df_f = df_f[df_f["Equipement"].isin(equipement)]
    if tag_sel:    df_f = df_f[df_f[tag_col].isin(tag_sel)]
    if specialite: df_f = df_f[df_f["Spécialité"].isin(specialite)]

    total     = len(df_f)
    pannes    = df_f[df_f["Categorie"] == "Correctif"]
    hs        = df_f[df_f["Statut opérationnel"] == "HS"]
    nb_pannes = len(pannes)
    nb_hs     = len(hs)
    dispo     = round((total - nb_hs) / total * 100, 1) if total else 0

    # ── DASHBOARD ──
    if menu == "Dashboard":
        page_header("🏠", "Tableau de bord Maintenance")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(kpi_card("op_total", "Interventions",      total,     "kpi-icon-blue"),  unsafe_allow_html=True)
        with c2: st.markdown(kpi_card("op_panne", "Pannes correctifs",  nb_pannes, "kpi-icon-red"),   unsafe_allow_html=True)
        with c3: st.markdown(kpi_card("op_hs",    "Équipements HS",     nb_hs,     "kpi-icon-red"),   unsafe_allow_html=True)
        with c4: st.markdown(kpi_card("op_dispo", "Disponibilité",      f"{dispo}%","kpi-icon-green", delta=f"{dispo-85:.1f}% vs cible 85%"), unsafe_allow_html=True)

        st.markdown("---")
        col_l, col_r = st.columns(2, gap="large")
        with col_l:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("##### Répartition par type d'opération")
            if not df_f.empty:
                vals   = df_f["Categorie"].value_counts()
                COLORS = ["#f97316","#2563eb","#16a34a","#ca8a04","#dc2626","#64748b"]
                fig = go.Figure(go.Pie(
                    labels=vals.index, values=vals.values, hole=0.55,
                    marker=dict(colors=COLORS, line=dict(color="#ffffff", width=2)),
                    textfont=dict(color="#1a2332"),
                ))
                fig.update_layout(**PLOTLY_LAYOUT, height=280)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("##### Évolution mensuelle des interventions")
            if not df_f.empty and df_f["Date"].notna().any():
                monthly = df_f.set_index("Date").resample("ME").size().reset_index()
                monthly.columns = ["Date","Interventions"]
                fig2 = px.line(monthly, x="Date", y="Interventions", color_discrete_sequence=["#f97316"])
                fig2.update_traces(line_width=2.5, mode="lines+markers", marker=dict(size=7, color="#f97316"))
                fig2.update_layout(**PLOTLY_LAYOUT, height=280)
                st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("##### Top 10 équipements — Pannes")
            if "Equipement" in df_f.columns and not pannes.empty:
                top = pannes["Equipement"].value_counts().head(10).reset_index()
                top.columns = ["Equipement","Pannes"]
                fig3 = px.bar(top, x="Pannes", y="Equipement", orientation="h", color_discrete_sequence=["#dc2626"])
                fig3.update_layout(**PLOTLY_LAYOUT, height=300, yaxis=dict(categoryorder="total ascending"))
                st.plotly_chart(fig3, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("##### Interventions par spécialité")
            if "Spécialité" in df_f.columns and not df_f.empty:
                spec = df_f["Spécialité"].value_counts().reset_index()
                spec.columns = ["Spécialité","Total"]
                fig4 = px.bar(spec, x="Spécialité", y="Total", color_discrete_sequence=["#2563eb"])
                fig4.update_layout(**PLOTLY_LAYOUT, height=300)
                st.plotly_chart(fig4, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── JOURNAL ──
    elif menu == "Journal":
        page_header("📋", "Journal des interventions")
        st.caption(f"{len(df_f)} enregistrement(s) trouvé(s)")
        st.dataframe(df_f.reset_index(drop=True), use_container_width=True, height=500)

    # ── ÉQUIPES ──
    elif menu == "Équipes":
        page_header("👷", "Gestion des équipes")
        if "Spécialité" in df_f.columns:
            spec_stats = df_f.groupby("Spécialité").agg(
                Interventions=("Spécialité","count"),
                Pannes=("Categorie", lambda x: (x=="Correctif").sum()),
            ).reset_index()
            spec_stats["% Correctif"] = (spec_stats["Pannes"] / spec_stats["Interventions"] * 100).round(1)
            st.dataframe(spec_stats, use_container_width=True)
            fig = px.bar(spec_stats, x="Spécialité", y="Interventions",
                         color="% Correctif", color_continuous_scale="RdYlGn_r")
            fig.update_layout(**PLOTLY_LAYOUT, height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Colonne 'Spécialité' non disponible.")

    # ── CRITICITÉ ──
    elif menu == "Criticité":

        page_header("⚠️", "Analyse de Criticité")

        st.markdown(
                "<p style='color:#64748b;'>Criticité = "
                "<b style='color:#f97316'>Fréquence × Gravité × Détectabilité</b></p>",
                unsafe_allow_html=True
        )

        st.markdown("---")
    
        if "Equipement" in df_f.columns and not df_f.empty:


            # ==============================
            # CONVERSION TEMPS D'ARRÊT
            # ==============================

            df_f["Temps arrêt"] = pd.to_timedelta(
                df_f["Temps arrêt"],
                errors="coerce"
            )

            # Remplacer vide par 0
            df_f["Temps arrêt"] = df_f["Temps arrêt"].fillna(
                pd.Timedelta(seconds=0)
            )

            # Conversion en heures
            df_f["Arret_h"] = (
                df_f["Temps arrêt"]
                .dt.total_seconds() / 3600
            )

            # ==============================
            # STATISTIQUES ÉQUIPEMENTS
            # ==============================

            equip_stats = df_f.groupby("Equipement").agg(
                Total_interventions=("Equipement", "count"),

                Nb_pannes=(
                    "Categorie",
                    lambda x: (x == "Correctif").sum()
                ),

                Nb_HS=(
                    "Statut opérationnel",
                    lambda x: (x == "HS").sum()
                ),

            ).reset_index()

            # ==============================
            # SCORE 1 → 5
            # ==============================

            def score_1_5(series):

                mn = series.min()
                mx = series.max()

                if mx == mn:
                    return pd.Series(
                        [3] * len(series),
                        index=series.index
                    )

                return (
                    ((series - mn) / (mx - mn) * 4) + 1
                ).round().astype(int)

            # ==============================
            # FRÉQUENCE
            # ==============================

            equip_stats["Freq_score"] = score_1_5(
                equip_stats["Nb_pannes"]
            )

            # ==============================
            # GRAVITÉ
            # ==============================

            # Temps d'arrêt moyen par équipement
            gravite = (
                df_f.groupby("Equipement")["Arret_h"]
                .mean()
                .reset_index()
            )

            equip_stats = equip_stats.merge(
                gravite,
                on="Equipement",
                how="left"
            )

            equip_stats["Grav_score"] = score_1_5(
                equip_stats["Arret_h"]
            )

            # ==============================
            # DÉTECTABILITÉ
            # ==============================

            prev_count = (
                df_f[df_f["Categorie"] == "Inspection"]
                .groupby("Equipement")
                .size()
                .reindex(
                    equip_stats["Equipement"],
                    fill_value=0
                )
            )

            equip_stats["Det_score"] = (
                6 - score_1_5(prev_count)
            ).clip(1, 5)

            # ==============================
            # CRITICITÉ GLOBALE
            # ==============================

            equip_stats["Criticite"] = (
                equip_stats["Freq_score"]
                * equip_stats["Grav_score"]
                * equip_stats["Det_score"]
            )

            # ==============================
            # NIVEAUX
            # ==============================

            def niveau_crit(c):

                if c >= 60:
                    return ("CRITIQUE", "badge-red")

                if c >= 30:
                    return ("ÉLEVÉE", "badge-orange")

                if c >= 15:
                    return ("MODÉRÉE", "badge-yellow")

                return ("FAIBLE", "badge-green")

            equip_stats[["Niveau", "Badge"]] = (
                equip_stats["Criticite"]
                .apply(lambda c: pd.Series(niveau_crit(c)))
            )

            equip_stats = equip_stats.sort_values(
                "Criticite",
                ascending=False
            )

            # ==============================
            # KPI
            # ==============================

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.markdown(
                    kpi_card(
                        "crit_rouge",
                        "CRITIQUE",
                        len(
                            equip_stats[
                                equip_stats["Niveau"] == "CRITIQUE"
                            ]
                        ),
                        "kpi-icon-red"
                    ),
                    unsafe_allow_html=True
                )

            with c2:
                st.markdown(
                    kpi_card(
                        "crit_elev",
                        "ÉLEVÉE",
                        len(
                            equip_stats[
                                equip_stats["Niveau"] == "ÉLEVÉE"
                            ]
                        ),
                        "kpi-icon-orange"
                    ),
                    unsafe_allow_html=True
                )

            with c3:
                st.markdown(
                    kpi_card(
                        "crit_mod",
                        "MODÉRÉE",
                        len(
                            equip_stats[
                                equip_stats["Niveau"] == "MODÉRÉE"
                            ]
                        ),
                        "kpi-icon-yellow"
                    ),
                    unsafe_allow_html=True
                )

            with c4:
                st.markdown(
                    kpi_card(
                        "crit_faib",
                        "FAIBLE",
                        len(
                            equip_stats[
                                equip_stats["Niveau"] == "FAIBLE"
                            ]
                        ),
                        "kpi-icon-green"
                    ),
                    unsafe_allow_html=True
                )

            st.markdown("---")

            # ==============================
            # TABLEAU + GRAPHIQUES
            # ==============================

            col_l, col_r = st.columns([3, 2], gap="large")

            with col_l:

                st.markdown(
                    '<div class="section-card">',
                    unsafe_allow_html=True
                )

                st.markdown(
                    "#### Tableau de criticité par équipement"
                )

                for _, row in equip_stats.iterrows():

                    badge_html = (
                        f'<span class="badge {row["Badge"]}">'
                        f'{row["Niveau"]}</span>'
                    )

                    st.markdown(
                        f"**{row['Equipement']}** "
                        f"&nbsp;{badge_html}&nbsp; — "
                        f"Score : `{row['Criticite']}` | "
                        f"Pannes : `{row['Nb_pannes']}` | "
                        f"F:`{row['Freq_score']}` "
                        f"G:`{row['Grav_score']}` "
                        f"D:`{row['Det_score']}`",
                        unsafe_allow_html=True
                    )

                    st.markdown("")

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            with col_r:

                st.markdown(
                    '<div class="section-card">',
                    unsafe_allow_html=True
                )

                CRIT_COLORS = {
                    "CRITIQUE": "#dc2626",
                    "ÉLEVÉE": "#f97316",
                    "MODÉRÉE": "#ca8a04",
                    "FAIBLE": "#16a34a"
                }

                niveaux = (
                    equip_stats["Niveau"]
                    .value_counts()
                    .reset_index()
                )

                niveaux.columns = ["Niveau", "Nb"]

                niveaux["Couleur"] = (
                    niveaux["Niveau"]
                    .map(CRIT_COLORS)
                )

                fig = go.Figure(
                    go.Bar(
                        x=niveaux["Niveau"],
                        y=niveaux["Nb"],
                        marker_color=niveaux["Couleur"],
                        text=niveaux["Nb"],
                        textposition="outside"
                    )
                )

                fig.update_layout(
                    **PLOTLY_LAYOUT,
                    height=280,
                    xaxis=dict(
                        categoryorder="array",
                        categoryarray=[
                            "CRITIQUE",
                            "ÉLEVÉE",
                            "MODÉRÉE",
                            "FAIBLE"
                        ]
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                top5 = equip_stats.head(5)[
                    ["Equipement", "Criticite", "Niveau"]
                ]

                fig2 = px.bar(
                    top5,
                    x="Equipement",
                    y="Criticite",
                    color="Niveau",
                    color_discrete_map=CRIT_COLORS
                )

                fig2.update_layout(
                    **PLOTLY_LAYOUT,
                    height=230,
                    showlegend=False
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            # ==============================
            # MATRICE RISQUE
            # ==============================

            st.markdown("---")

            st.markdown(
                '<div class="section-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                "#### Matrice de risque Fréquence × Gravité"
            )

            # Nettoyage des valeurs NaN
            equip_stats["Criticite"] = (
                pd.to_numeric(
                    equip_stats["Criticite"],
                    errors="coerce"
                )
                .fillna(1)
            )

            equip_stats["Freq_score"] = (
                pd.to_numeric(
                    equip_stats["Freq_score"],
                    errors="coerce"
                )
                .fillna(1)
            )

            equip_stats["Grav_score"] = (
                pd.to_numeric(
                    equip_stats["Grav_score"],
                    errors="coerce"
                )
                .fillna(1)
            )

            fig_m = px.scatter(
                equip_stats,
                x="Freq_score",
                y="Grav_score",
                size="Criticite",
                color="Niveau",
                color_discrete_map=CRIT_COLORS,
                hover_name="Equipement",
                size_max=50,
                labels={
                    "Freq_score": "Fréquence (1-5)",
                    "Grav_score": "Gravité (1-5)"
                }
            )

            fig_m.update_layout(
                **PLOTLY_LAYOUT,
                height=400,
                xaxis=dict(
                    range=[0.5, 5.5],
                    tickvals=[1, 2, 3, 4, 5]
                ),
                yaxis=dict(
                    range=[0.5, 5.5],
                    tickvals=[1, 2, 3, 4, 5]
                )
            )

            st.plotly_chart(
                fig_m,
                use_container_width=True
            )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

        else:
         st.warning("Aucune donnée disponible.")

    # ── PRÉDICTIF — utilise "Tag" (journal) ──
    elif menu == "Prédictif":
        page_header("🔮", "Maintenance Prédictive")
        st.markdown("<p style='color:#64748b;'>Prévision basée sur le MTBF historique par Tag.</p>", unsafe_allow_html=True)

        tag_col_j = COL_TAG_JOURNAL  # "Tag"
        if not pannes.empty and tag_col_j in pannes.columns:
            p = pannes.sort_values([tag_col_j, "Date"])
            p["Intervalle"] = p.groupby(tag_col_j)["Date"].diff().dt.days

            pred = pd.DataFrame({
                "Dernière panne": p.groupby(tag_col_j)["Date"].max(),
                "MTBF (jours)":   p.groupby(tag_col_j)["Intervalle"].mean().round(1),
                "Nb pannes":      p.groupby(tag_col_j).size(),
            }).dropna(subset=["Dernière panne"])

            pred["MTBF (jours)"] = pd.to_numeric(pred["MTBF (jours)"], errors="coerce").fillna(30)
            pred["Prochaine panne estimée"] = pred["Dernière panne"] + pd.to_timedelta(pred["MTBF (jours)"], unit="D")
            pred["Jours restants"] = (pred["Prochaine panne estimée"] - pd.Timestamp.now()).dt.days.astype(int)

            def alerte(j):
                if j < 0:  return ("⛔ DÉPASSÉ", "badge-red")
                if j < 15: return ("🔴 URGENT",  "badge-red")
                if j < 30: return ("🟠 BIENTÔT", "badge-orange")
                return             ("🟢 OK",       "badge-green")

            pred[["Alerte","Badge"]] = pred["Jours restants"].apply(lambda j: pd.Series(alerte(j)))
            pred = pred.sort_values("Jours restants")

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(kpi_card("mtbf",   "Tags analysés",       len(pred),                                   "kpi-icon-blue"),   unsafe_allow_html=True)
            with c2: st.markdown(kpi_card("urgent", "Urgentes (< 15j)",    len(pred[pred["Jours restants"] < 15]),      "kpi-icon-red"),    unsafe_allow_html=True)
            with c3: st.markdown(kpi_card("jours",  "MTBF moyen",          f"{pred['MTBF (jours)'].mean():.0f} j",      "kpi-icon-purple"), unsafe_allow_html=True)

            st.markdown("---")
            col_l, col_r = st.columns([2, 1], gap="large")
            with col_l:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                display = pred.reset_index()
                # Renommer l'index "Tag" pour l'affichage
                display = display.rename(columns={tag_col_j: "Tag"})
                display = display[["Tag","Nb pannes","MTBF (jours)","Dernière panne","Prochaine panne estimée","Jours restants","Alerte"]]
                st.dataframe(display, use_container_width=True, height=400)
                st.markdown('</div>', unsafe_allow_html=True)
            with col_r:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown("#### Alertes")
                urgent = pred[pred["Jours restants"] < 30]
                if urgent.empty:
                    st.success("Aucune intervention urgente dans les 30 prochains jours.")
                for tag_id, row in urgent.iterrows():
                    badge_html = f'<span class="badge {row["Badge"]}">{row["Alerte"]}</span>'
                    st.markdown(f"**{tag_id}** &nbsp; {badge_html}<br><small style='color:#64748b'>Dans {row['Jours restants']} jours — MTBF {row['MTBF (jours)']} j</small>", unsafe_allow_html=True)
                    st.markdown("")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Aucune donnée de pannes disponible.")

    # ── RAPPORTS ──
    elif menu == "Rapports":
        page_header("📄", "Génération de rapports")
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### Export Excel")
            if st.button("⬇ Télécharger Excel", use_container_width=True):
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df_f.to_excel(writer, sheet_name="Journal", index=False)
                    if not pannes.empty:
                        pannes.to_excel(writer, sheet_name="Pannes", index=False)
                st.download_button("📥 Sauvegarder Excel", buf.getvalue(),
                                   file_name=f"rapport_maintenance_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### Export PDF")
            if st.button("📄 Générer PDF", use_container_width=True):
                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=18, spaceAfter=6, textColor=colors.HexColor("#f97316"))
                elements = []
                try: elements.append(RLImage("logo.png", width=3.5*cm, height=1.8*cm))
                except: pass
                elements.append(Spacer(1, 0.3*cm))
                elements.append(Paragraph("RAPPORT DE MAINTENANCE — TRIDENT-OGX", title_style))
                periode = (f"{date_range[0]} au {date_range[1]}" if len(date_range)==2 else "Toutes les données")
                elements.append(Paragraph(f"Période : {periode}", styles["Normal"]))
                elements.append(Paragraph(f"Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
                elements.append(Spacer(1, 0.5*cm))
                kpi_data = [["Indicateur","Valeur"],
                             ["Total interventions", str(total)],
                             ["Pannes (correctif)", str(nb_pannes)],
                             ["Équipements HS", str(nb_hs)],
                             ["Disponibilité", f"{dispo:.1f}%"]]
                tbl = Table(kpi_data, colWidths=[7*cm, 5*cm])
                tbl.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#f97316")),
                    ("TEXTCOLOR", (0,0),(-1,0), colors.white),
                    ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
                    ("GRID",      (0,0),(-1,-1), 0.5, colors.HexColor("#d1d5db")),
                    ("ALIGN",     (1,0),(1,-1), "CENTER"),
                    ("PADDING",   (0,0),(-1,-1), 8),
                ]))
                elements.append(tbl)
                elements.append(Spacer(1, 0.5*cm))
                if not df_f.empty:
                    cols_exp = [c for c in ["Date","Tag","Equipement","Type d'opération","Spécialité","Statut opérationnel"] if c in df_f.columns]
                    df_exp = df_f[cols_exp].head(50)
                    rows = [cols_exp] + df_exp.values.tolist()
                    tbl2 = Table(rows, repeatRows=1)
                    tbl2.setStyle(TableStyle([
                        ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#1a2332")),
                        ("TEXTCOLOR", (0,0),(-1,0), colors.HexColor("#f97316")),
                        ("FONTSIZE",  (0,0),(-1,-1), 7),
                        ("GRID",      (0,0),(-1,-1), 0.4, colors.HexColor("#d1d5db")),
                        ("PADDING",   (0,0),(-1,-1), 4),
                    ]))
                    elements.append(tbl2)
                doc.build(elements)
                st.download_button("📥 Sauvegarder PDF", buf.getvalue(),
                                   file_name=f"rapport_maintenance_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                   mime="application/pdf")
            st.markdown('</div>', unsafe_allow_html=True)

# ===========================
#  MODULE PLANNING
# ===========================
if st.session_state["module"] == "planning":
    back_button()
    page_header("📅", "Planning Maintenance")

    df_plan = load_planning()
    df_plan["Début"] = pd.to_datetime(df_plan["Début"], errors="coerce", dayfirst=True)
    df_plan["Fin"]   = pd.to_datetime(df_plan["Fin"],   errors="coerce", dayfirst=True)
    df_plan = df_plan.dropna(subset=["Début","Fin"])

    planning_rows = []
    for (semaine, spec), group in df_plan.groupby(["Semaine","Spécialité"]):
        debut, fin = group["Début"].min(), group["Fin"].max()
        if pd.isna(debut) or pd.isna(fin): continue
        jours = pd.date_range(debut, fin)
        if len(jours) == 0: continue
        group = group.sort_values("Equipement").reset_index(drop=True)
        nb_taches, nb_jours = len(group), len(jours)
        base, reste = nb_taches // nb_jours, nb_taches % nb_jours
        idx = 0
        for i, jour in enumerate(jours):
            for _ in range(base + (1 if i < reste else 0)):
                if idx >= nb_taches: break
                row = group.iloc[idx]
                planning_rows.append({
                    "Date":       jour,
                    "Equipement": row.get("Equipement",""),
                    "TAG":        row.get(COL_TAG_PLANNING,""),  # "TAG" = planning
                    "Tâche":      row.get("Description",""),
                    "Spécialité": row.get("Spécialité",""),
                    "Semaine":    semaine,
                    "Statut":     "Planifié",
                })
                idx += 1

    planning = pd.DataFrame(planning_rows)
    if planning.empty:
        st.error("Aucun planning généré.")
        st.stop()

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1: annee = st.selectbox("Année", sorted(planning["Date"].dt.year.unique()))
    with col_f2: mois  = st.selectbox("Mois", list(range(1,13)), format_func=lambda m: dt.date(2000,m,1).strftime("%B").capitalize())
    with col_f3: spec_filtre = st.multiselect("Spécialité", planning["Spécialité"].dropna().unique())

    date_debut = dt.datetime(annee, mois, 1)
    date_fin   = dt.datetime(annee+1,1,1) if mois==12 else dt.datetime(annee,mois+1,1)
    p_mois = planning[(planning["Date"] >= date_debut) & (planning["Date"] < date_fin)]
    if spec_filtre: p_mois = p_mois[p_mois["Spécialité"].isin(spec_filtre)]

    st.markdown("---")
    total_t    = len(p_mois)
    jours_pl   = p_mois["Date"].nunique()
    charge_moy = round(total_t / jours_pl, 1) if jours_pl else 0

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(kpi_card("planning","Tâches planifiées", total_t,    "kpi-icon-blue"),   unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("jours",   "Jours actifs",      jours_pl,   "kpi-icon-purple"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("charge",  "Charge moy./jour",  charge_moy, "kpi-icon-orange"), unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns([3,2], gap="large")
    with col_l:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Planning mensuel")
        st.dataframe(p_mois.sort_values("Date").reset_index(drop=True), use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_r:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        if not p_mois.empty:
            charge_j = p_mois.groupby("Date").size().reset_index(name="Tâches")
            fig = px.bar(charge_j, x="Date", y="Tâches", color_discrete_sequence=["#2563eb"])
            fig.update_layout(**PLOTLY_LAYOUT, height=220)
            st.plotly_chart(fig, use_container_width=True)
        if not p_mois.empty and "Spécialité" in p_mois.columns:
            sp = p_mois["Spécialité"].value_counts().reset_index()
            sp.columns = ["Spécialité","Tâches"]
            fig2 = px.pie(sp, names="Spécialité", values="Tâches", hole=0.5,
                          color_discrete_sequence=["#f97316","#2563eb","#16a34a","#ca8a04"])
            fig2.update_layout(**PLOTLY_LAYOUT, height=220)
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("⬇ Exporter planning mensuel Excel"):
        buf = io.BytesIO()
        p_mois.to_excel(buf, index=False)
        st.download_button("📥 Sauvegarder", buf.getvalue(),
                           file_name=f"planning_{annee}_{mois:02d}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ===========================
#  MODULE DIRECTION
# ===========================
if st.session_state["module"] == "direction":
    back_button()
    page_header("📊", "Dashboard Direction")

    total_d  = len(df)
    pannes_d = df[df["Categorie"] == "Correctif"]
    # Correction logique disponibilité : basée sur équipements uniques
    if "Statut opérationnel" in df.columns:
        hs_d = df[df["Statut opérationnel"] == "HS"]
    else:
        hs_d = pd.DataFrame()
    eq_total = df["Equipement"].nunique() if "Equipement" in df.columns else 0
    eq_hs    = df[df["Statut opérationnel"] == "HS"]["Equipement"].nunique() if ("Statut opérationnel" in df.columns and "Equipement" in df.columns) else 0
    dispo_d  = round((eq_total - eq_hs) / eq_total * 100, 1) if eq_total else 0
    taux_c_d = round(len(pannes_d) / total_d * 100, 1) if total_d else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(kpi_card("op_total","Total interventions", total_d,         "kpi-icon-blue"),   unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("op_panne","Pannes correctifs",   len(pannes_d),   "kpi-icon-red"),    unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("op_hs",   "Équipements HS",      len(hs_d),       "kpi-icon-red"),    unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("op_dispo","Disponibilité",        f"{dispo_d}%",   "kpi-icon-green",  delta=f"{dispo_d-85:.1f}% vs objectif"),  unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("taux",    "Taux correctif",       f"{taux_c_d}%", "kpi-icon-purple", delta="Cible ≤ 30%"), unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2, gap="large")
    with col_l:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        monthly_p = pannes_d.set_index("Date").resample("ME").size().reset_index()
        monthly_p.columns = ["Date","Pannes"]
        fig = px.area(monthly_p, x="Date", y="Pannes", color_discrete_sequence=["#dc2626"])
        fig.update_layout(**PLOTLY_LAYOUT, height=280)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_r:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        if "Equipement" in df.columns:
            eq_total = df.groupby("Equipement").size()
            eq_hs    = df[df["Statut opérationnel"]=="HS"].groupby("Equipement").size()
            eq_dispo = ((eq_total - eq_hs.reindex(eq_total.index, fill_value=0)) / eq_total * 100).round(1)
            eq_dispo = eq_dispo.sort_values().head(10).reset_index()
            eq_dispo.columns = ["Equipement","Disponibilité (%)"]
            fig2 = px.bar(eq_dispo, x="Disponibilité (%)", y="Equipement", orientation="h",
                          color="Disponibilité (%)", color_continuous_scale="RdYlGn", range_color=[50,100])
            fig2.update_layout(**PLOTLY_LAYOUT, height=280, yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b, col_c = st.columns(3, gap="large")
    with col_a:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        cat_count = df["Categorie"].value_counts().reset_index()
        cat_count.columns = ["Catégorie","Total"]
        fig3 = px.pie(cat_count, names="Catégorie", values="Total", hole=0.55,
                      color_discrete_sequence=["#f97316","#2563eb","#16a34a","#ca8a04","#dc2626","#64748b"])
        fig3.update_layout(**PLOTLY_LAYOUT, height=280)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        if "Spécialité" in df.columns:
            sp = df["Spécialité"].value_counts().reset_index()
            sp.columns = ["Spécialité","Nb"]
            fig4 = px.bar(sp, x="Nb", y="Spécialité", orientation="h", color_discrete_sequence=["#2563eb"])
            fig4.update_layout(**PLOTLY_LAYOUT, height=280, yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        color_dispo = "#16a34a" if dispo_d >= 85 else "#dc2626"
        color_taux  = "#16a34a" if taux_c_d <= 30 else "#dc2626"
        nb_equips   = df["Equipement"].nunique() if "Equipement" in df.columns else "—"
        st.markdown(f"""
        <div>
            <p style='color:#64748b;font-size:0.8rem;margin:0;text-transform:uppercase;letter-spacing:1px;'>DISPONIBILITÉ</p>
            <p style='font-family:Rajdhani;font-size:2.2rem;font-weight:700;margin:0;color:{color_dispo};'>{dispo_d}%</p>
            <p style='color:#64748b;font-size:0.75rem;margin-bottom:1rem;'>Cible : 85%</p>
            <p style='color:#64748b;font-size:0.8rem;margin:0;text-transform:uppercase;letter-spacing:1px;'>TAUX CORRECTIF</p>
            <p style='font-family:Rajdhani;font-size:2.2rem;font-weight:700;margin:0;color:{color_taux};'>{taux_c_d}%</p>
            <p style='color:#64748b;font-size:0.75rem;margin-bottom:1rem;'>Cible : ≤ 30%</p>
            <p style='color:#64748b;font-size:0.8rem;margin:0;text-transform:uppercase;letter-spacing:1px;'>ÉQUIPEMENTS SUIVIS</p>
            <p style='font-family:Rajdhani;font-size:2.2rem;font-weight:700;margin:0;color:#2563eb;'>{nb_equips}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ===========================
#  MODULE GESTION ÉQUIPEMENTS
#  Source : planning_annuel.xlsx
# ===========================
if st.session_state["module"] == "gestion_equip":
    back_button()
    page_header("🗂️", "Gestion des Équipements")

    # ── Init base depuis planning_annuel.xlsx (source = planning, pas journal) ──
    if st.session_state["equipements_db"] is None:
        df_plan_src = load_planning()
        cols_needed = ["Equipement", COL_TAG_PLANNING, "Spécialité", "Site", "Zone", "Criticité", "Fabricant"]
        existing    = [c for c in cols_needed if c in df_plan_src.columns]

        if "Equipement" in df_plan_src.columns:
            equip_init = df_plan_src[existing].drop_duplicates(subset=["Equipement"]).copy()
            # Renommer TAG → TAG principal, Spécialité → Spécialité principale
            rename_map = {COL_TAG_PLANNING: "TAG principal", "Spécialité": "Spécialité principale"}
            equip_init = equip_init.rename(columns=rename_map)

            defaults = {
                "TAG principal":         "",
                "Spécialité principale": "",
                "Site":                  "",
                "Zone":                  "",
                "Statut":                "Opérationnel",
                "Criticité":             "Modérée",
                "Fabricant":             "",
                "N° Série":              "",
                "Mise en service":       "",
                "Notes":                 "",
            }
            for col, default in defaults.items():
                if col not in equip_init.columns:
                    equip_init[col] = default

            final_cols = ["Equipement","TAG principal","Spécialité principale","Site","Zone",
                          "Statut","Criticité","Fabricant","N° Série","Mise en service","Notes"]
            equip_init = equip_init.reindex(columns=final_cols, fill_value="")
            st.session_state["equipements_db"] = equip_init.reset_index(drop=True)
        else:
            st.session_state["equipements_db"] = pd.DataFrame(columns=[
                "Equipement","TAG principal","Spécialité principale","Site","Zone",
                "Statut","Criticité","Fabricant","N° Série","Mise en service","Notes"
            ])

    db = st.session_state["equipements_db"].copy()

    menu_ge = st.sidebar.radio("Action", ["📋 Liste", "➕ Ajouter", "✏️ Modifier", "🗑️ Supprimer"])
    st.sidebar.markdown("---")

    STATUTS    = ["Opérationnel","HS","En révision","En attente pièces","Mis au rebut"]
    CRITICITES = ["Faible","Modérée","Élevée","Critique"]

    # ── LISTE ──
    if menu_ge == "📋 Liste":
        st.markdown(f"<p style='color:#64748b;'>{len(db)} équipement(s) — source : <b>planning_annuel.xlsx</b></p>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        f_statut = c1.multiselect("Statut",    STATUTS)
        f_crit   = c2.multiselect("Criticité", CRITICITES)
        f_search = c3.text_input("Recherche",  placeholder="Nom, TAG...")

        db_view = db.copy()
        if f_statut: db_view = db_view[db_view["Statut"].isin(f_statut)]
        if f_crit:   db_view = db_view[db_view["Criticité"].isin(f_crit)]
        if f_search:
            mask = db_view.apply(lambda r: f_search.lower() in str(r).lower(), axis=1)
            db_view = db_view[mask]

        st.dataframe(db_view.reset_index(drop=True), use_container_width=True, height=420)

        st.markdown("---")
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(kpi_card("equip",     "Total équipements", len(db),                                                          "kpi-icon-blue"),   unsafe_allow_html=True)
        with k2: st.markdown(kpi_card("op_dispo",  "Opérationnels",     len(db[db["Statut"]=="Opérationnel"]) if "Statut" in db.columns else 0, "kpi-icon-green"), unsafe_allow_html=True)
        with k3: st.markdown(kpi_card("op_hs",     "HS",                len(db[db["Statut"]=="HS"]) if "Statut" in db.columns else 0,          "kpi-icon-red"),   unsafe_allow_html=True)
        with k4: st.markdown(kpi_card("crit_rouge","Critiques",         len(db[db["Criticité"]=="Critique"]) if "Criticité" in db.columns else 0, "kpi-icon-red"), unsafe_allow_html=True)

        col_l, col_r = st.columns(2, gap="large")
        with col_l:
            if "Statut" in db.columns and not db.empty:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                s = db["Statut"].value_counts().reset_index(); s.columns = ["Statut","Nb"]
                fig = px.pie(s, names="Statut", values="Nb", hole=0.5,
                             color_discrete_sequence=["#16a34a","#dc2626","#ca8a04","#2563eb","#64748b"])
                fig.update_layout(**PLOTLY_LAYOUT, height=250)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        with col_r:
            if "Criticité" in db.columns and not db.empty:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                c_df = db["Criticité"].value_counts().reset_index(); c_df.columns = ["Criticité","Nb"]
                CRIT_COL = {"Critique":"#dc2626","Élevée":"#f97316","Modérée":"#ca8a04","Faible":"#16a34a"}
                fig2 = px.bar(c_df, x="Criticité", y="Nb", color="Criticité", color_discrete_map=CRIT_COL)
                fig2.update_layout(**PLOTLY_LAYOUT, height=250, showlegend=False,
                                   xaxis=dict(categoryorder="array", categoryarray=["Critique","Élevée","Modérée","Faible"]))
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("⬇ Exporter la base équipements"):
            buf = io.BytesIO()
            db.to_excel(buf, index=False)
            st.download_button("📥 Sauvegarder Excel", buf.getvalue(),
                               file_name="equipements.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ── AJOUTER ──
    elif menu_ge == "➕ Ajouter":
        page_header("➕", "Ajouter un équipement")
        with st.form("form_ajout"):
            c1, c2 = st.columns(2)
            nom  = c1.text_input("Nom équipement *", placeholder="Ex: Pompe centrifuge P-101")
            tag  = c2.text_input("TAG principal *",  placeholder="Ex: TAG-042")
            c3, c4 = st.columns(2)
            site = c3.text_input("Site / Unité", placeholder="Ex: Unité A")
            zone = c4.text_input("Zone",         placeholder="Ex: Zone Nord")
            c5, c6 = st.columns(2)
            spec   = c5.selectbox("Spécialité", ["Mécanique","Électrique","Instrumentation","Hydraulique","Autre"])
            statut = c6.selectbox("Statut",     STATUTS)
            c7, c8 = st.columns(2)
            crit   = c7.selectbox("Criticité",  CRITICITES)
            fab    = c8.text_input("Fabricant",  placeholder="Ex: Grundfos")
            c9, c10 = st.columns(2)
            serie   = c9.text_input("N° Série",        placeholder="Ex: SN-20240001")
            mise_en = c10.text_input("Mise en service", placeholder="Ex: 15/03/2020")
            notes   = st.text_area("Notes / Observations", height=80)
            submitted = st.form_submit_button("✅ Enregistrer l'équipement", use_container_width=True)

        if submitted:
            if not nom or not tag:
                st.error("Le nom et le TAG sont obligatoires.")
            elif nom in db["Equipement"].values:
                st.warning(f"L'équipement '{nom}' existe déjà.")
            else:
                new_row = {"Equipement":nom,"TAG principal":tag,"Spécialité principale":spec,
                           "Site":site,"Zone":zone,"Statut":statut,"Criticité":crit,
                           "Fabricant":fab,"N° Série":serie,"Mise en service":mise_en,"Notes":notes}
                st.session_state["equipements_db"] = pd.concat([db, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"✅ Équipement **{nom}** ajouté !")
                st.rerun()

    # ── MODIFIER ──
    elif menu_ge == "✏️ Modifier":
        page_header("✏️", "Modifier un équipement")
        if db.empty:
            st.info("Aucun équipement dans la base.")
        else:
            equip_sel = st.selectbox("Sélectionner l'équipement", db["Equipement"].tolist())
            idx = db[db["Equipement"] == equip_sel].index[0]
            row = db.loc[idx]
            with st.form("form_modif"):
                c1, c2 = st.columns(2)
                nom  = c1.text_input("Nom équipement *", value=str(row.get("Equipement","")))
                tag  = c2.text_input("TAG principal *",  value=str(row.get("TAG principal","")))
                c3, c4 = st.columns(2)
                site = c3.text_input("Site / Unité", value=str(row.get("Site","")))
                zone = c4.text_input("Zone",          value=str(row.get("Zone","")))
                c5, c6 = st.columns(2)
                spec_opts = ["Mécanique","Électrique","Instrumentation","Hydraulique","Autre"]
                cur_spec  = str(row.get("Spécialité principale","Mécanique"))
                spec   = c5.selectbox("Spécialité", spec_opts, index=spec_opts.index(cur_spec) if cur_spec in spec_opts else 0)
                cur_st = str(row.get("Statut","Opérationnel"))
                statut = c6.selectbox("Statut", STATUTS, index=STATUTS.index(cur_st) if cur_st in STATUTS else 0)
                c7, c8 = st.columns(2)
                cur_cr = str(row.get("Criticité","Modérée"))
                crit   = c7.selectbox("Criticité", CRITICITES, index=CRITICITES.index(cur_cr) if cur_cr in CRITICITES else 0)
                fab    = c8.text_input("Fabricant", value=str(row.get("Fabricant","")))
                c9, c10 = st.columns(2)
                serie   = c9.text_input("N° Série",        value=str(row.get("N° Série","")))
                mise_en = c10.text_input("Mise en service", value=str(row.get("Mise en service","")))
                notes   = st.text_area("Notes", value=str(row.get("Notes","")), height=80)
                submitted = st.form_submit_button("💾 Enregistrer les modifications", use_container_width=True)

            if submitted:
                st.session_state["equipements_db"].loc[idx] = {
                    "Equipement":nom,"TAG principal":tag,"Spécialité principale":spec,
                    "Site":site,"Zone":zone,"Statut":statut,"Criticité":crit,
                    "Fabricant":fab,"N° Série":serie,"Mise en service":mise_en,"Notes":notes
                }
                st.success(f"✅ **{nom}** mis à jour !")
                st.rerun()

    # ── SUPPRIMER ──
    elif menu_ge == "🗑️ Supprimer":
        page_header("🗑️", "Supprimer un équipement")
        if db.empty:
            st.info("Aucun équipement dans la base.")
        else:
            equip_sel = st.selectbox("Sélectionner l'équipement à supprimer", db["Equipement"].tolist())
            row = db[db["Equipement"] == equip_sel].iloc[0]
            st.markdown(f"""
            <div style='background:#fef2f2;border:1px solid #dc2626;border-radius:10px;padding:1.2rem;margin:1rem 0;'>
                <p style='color:#dc2626;font-weight:700;margin:0;'>⚠️ Confirmation de suppression</p>
                <p style='color:#1a2332;margin:0.5rem 0 0;'>Équipement : <b>{equip_sel}</b></p>
                <p style='color:#64748b;font-size:0.85rem;margin:0;'>TAG : {row.get("TAG principal","—")} | Statut : {row.get("Statut","—")}</p>
            </div>
            """, unsafe_allow_html=True)
            col_ok, col_ann = st.columns(2)
            if col_ok.button("🗑️ Confirmer la suppression", use_container_width=True):
                st.session_state["equipements_db"] = db[db["Equipement"] != equip_sel].reset_index(drop=True)
                st.success(f"Équipement **{equip_sel}** supprimé.")
                st.rerun()
            if col_ann.button("↩ Annuler", use_container_width=True):
                st.rerun()

# ===========================
#  MODULE SUIVI D'EXÉCUTION
#  Journal (Tag) vs Planning (TAG)
# ===========================
if st.session_state["module"] == "suivi_execution":

    back_button()

    page_header("📈", "Suivi d'Exécution — Journal vs Planning")

    st.markdown(
        "<p style='color:#64748b;'>Comparaison entre les tâches planifiées (planning_annuel) et les interventions réalisées (journal).</p>",
        unsafe_allow_html=True
    )

    # ── Préparation planning ─────────────────────────────

    df_plan = load_planning()

    df_plan["Début"] = pd.to_datetime(
        df_plan["Début"],
        errors="coerce",
        dayfirst=True
    )

    df_plan["Fin"] = pd.to_datetime(
        df_plan["Fin"],
        errors="coerce",
        dayfirst=True
    )

    df_plan = df_plan.dropna(subset=["Début", "Fin"])

    plan_rows = []

    for _, row in df_plan.iterrows():

        debut = row["Début"]
        fin = row["Fin"]

        if pd.isna(debut) or pd.isna(fin):
            continue

        plan_rows.append({
          "Date_plan": debut,
          "Mois_plan": debut.month,
          "Semaine_plan": int(debut.isocalendar().week),
          "Equipement": row.get("Equipement", ""),
          "TAG": row.get(COL_TAG_PLANNING, ""),
          "Tâche": row.get("Description", ""),
          "Spécialité": row.get("Spécialité", ""),
         })

    planning = pd.DataFrame(plan_rows)

    if planning.empty:
        st.warning("Aucune donnée de planning disponible.")
        st.stop()

    # ── Journal ──────────────────────────────────────────

    journal = df.copy()

    # Harmonisation des spécialités

    mapping_spec = {
        "Elect": "Electricité",
        "Méca": "Mécanique",
        "Instrum": "Instrum"
    }

    # Journal

    journal["Spécialité"] = (
        journal["Spécialité"]
        .astype(str)
        .str.strip()
        .replace(mapping_spec)
    )

    # Planning

    planning["Spécialité"] = (
        planning["Spécialité"]
        .astype(str)
        .str.strip()
    )

    # Harmonisation des TAG

    planning["TAG"] = (
        planning["TAG"]
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(" ", "", regex=False)
    )

    journal["Tag"] = (
        journal["Tag"]
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(" ", "", regex=False)
    )

    # Dates journal

    journal["Date"] = pd.to_datetime(
        journal["Date"],
        errors="coerce"
    )

    journal = journal.dropna(subset=["Date"])

    journal["Mois"] = journal["Date"].dt.month

    journal["Semaine"] = (
        journal["Date"]
        .dt.isocalendar()
        .week
        .fillna(0)
        .astype(int)
    )

    # ── Rapprochement Planning / Journal ─────────────────

    if "TAG" in planning.columns and "Tag" in journal.columns:

        comparaison = pd.merge(
            planning,
            journal[[
                "Tag",
                "Equipement",
                "Spécialité",
                "Date"
            ]].rename(columns={
                "Tag": "TAG",
                "Date": "Date_realise"
            }),

            left_on=["TAG", "Spécialité"],
            right_on=["TAG", "Spécialité"],
            how="left",
            suffixes=("", "_journal")
        )

    else:
        comparaison = planning.copy()

    # ── FILTRES ──────────────────────────────────────────

    st.markdown("---")

    cf1, cf2, cf3 = st.columns(3)

    annee_s = cf1.selectbox(
        "Année",
        sorted(planning["Date_plan"].dt.year.unique()),
        key="se_annee"
    )

    mois_s = cf2.selectbox(
        "Mois",
        list(range(1, 13)),
        key="se_mois",
        format_func=lambda m: dt.date(2000, m, 1).strftime("%B").capitalize()
    )

    spec_s = cf3.multiselect(
        "Spécialité",
        sorted(planning["Spécialité"].dropna().unique()),
        key="se_spec"
    )

    date_deb = dt.datetime(annee_s, mois_s, 1)

    date_fin_m = (
        dt.datetime(annee_s + 1, 1, 1)
        if mois_s == 12
        else dt.datetime(annee_s, mois_s + 1, 1)
    )

    # Planning mensuel

    plan_m = planning[
        (planning["Date_plan"] >= date_deb) &
        (planning["Date_plan"] < date_fin_m)
    ].copy()

    # Journal total

    jour_total = journal[
        (journal["Date"] >= date_deb) &
        (journal["Date"] < date_fin_m)
    ].copy()

    # Seulement les préventifs

    jour_m = journal[
        (journal["Date"] >= date_deb) &
        (journal["Date"] < date_fin_m) &
        (journal["Categorie"] == "Préventif")
    ].copy()

    # Filtre spécialité

    if spec_s:

        plan_m = plan_m[
            plan_m["Spécialité"].isin(spec_s)
        ]

        if "Spécialité" in jour_m.columns:

            jour_m = jour_m[
                jour_m["Spécialité"].isin(spec_s)
            ]

    # ── KPI Calculs ──────────────────────────────────────

    nb_planifie = len(plan_m)

    nb_realise = len(jour_m)

    nb_correctif_m = len(
        jour_total[jour_total["Categorie"] == "Correctif"]
    )

    nb_travaux_m = len(
        jour_total[jour_total["Categorie"] == "Travaux"]
    )

    nb_autres_m = len(
        jour_total[
            ~jour_total["Categorie"].isin([
                "Préventif",
                "Correctif",
                "Travaux"
            ])
        ]
    )

    nb_retard = max(0, nb_planifie - nb_realise)

    # Taux exécution

    if nb_planifie > 0:
        taux_exec = round(
            (nb_realise / nb_planifie) * 100,
            1
        )
    else:
        taux_exec = 0

    # Charge corrective

    if nb_planifie > 0:
        taux_urgence = round(
            (nb_correctif_m / nb_planifie) * 100,
            1
        )
    else:
        taux_urgence = 0

    # ── KPIs ─────────────────────────────────────────────

    st.markdown("---")

    k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)

    with k1:
        st.markdown(
            kpi_card(
                "planning",
                "Préventifs planifiés",
                nb_planifie,
                "kpi-icon-blue"
            ),
            unsafe_allow_html=True
        )

    with k2:
        st.markdown(
            kpi_card(
                "realise",
                "Préventifs réalisés",
                nb_realise,
                "kpi-icon-green"
            ),
            unsafe_allow_html=True
        )

    with k3:
        st.markdown(
            kpi_card(
                "taux",
                "Taux exécution",
                f"{taux_exec}%",
                "kpi-icon-purple"
            ),
            unsafe_allow_html=True
        )

    with k4:
        st.markdown(
            kpi_card(
                "retard",
                "Préventifs reportés",
                nb_retard,
                "kpi-icon-yellow"
            ),
            unsafe_allow_html=True
        )

    with k5:
        st.markdown(
            kpi_card(
                "correctif",
                "Correctifs",
                nb_correctif_m,
                "kpi-icon-red"
            ),
            unsafe_allow_html=True
        )

    with k6:
        st.markdown(
            kpi_card(
                "travaux",
                "Travaux",
                nb_travaux_m,
                "kpi-icon-orange"
            ),
            unsafe_allow_html=True
        )

    with k7:
        st.markdown(
            kpi_card(
                "autres",
                "Autres activités",
                nb_autres_m,
                "kpi-icon-blue"
            ),
            unsafe_allow_html=True
        )

    with k8:
        st.markdown(
            kpi_card(
                "urgence",
                "Charge corrective",
                f"{taux_urgence}%",
                "kpi-icon-red"
            ),
            unsafe_allow_html=True
        )

    # ── Alertes ──────────────────────────────────────────

    if taux_exec < 80 and nb_correctif_m > nb_realise:

        st.warning(
            "⚠️ Le faible taux d’exécution du préventif semble lié à une forte charge corrective."
        )

    backlog = nb_planifie - nb_realise

    st.info(
        f"Backlog maintenance : {backlog} tâche(s) préventive(s) non exécutée(s)."
    )

    # ── JAUGE + COMPARAISON HEBDO ──
    st.markdown("---")
    col_gauge, col_bar = st.columns([1, 2], gap="large")

    with col_gauge:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Taux d'exécution global")
        color_gauge = "#16a34a" if taux_exec >= 80 else ("#ca8a04" if taux_exec >= 50 else "#dc2626")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=taux_exec,
            number={"suffix":"%","font":{"color":"#1a2332","size":36}},
            gauge={
                "axis": {"range":[0,100],"tickcolor":"#64748b"},
                "bar":  {"color": color_gauge},
                "bgcolor": "#f0f2f5",
                "steps": [
                    {"range":[0,50],  "color":"#fee2e2"},
                    {"range":[50,80], "color":"#fef9c3"},
                    {"range":[80,100],"color":"#dcfce7"},
                ],
                "threshold": {"line":{"color":"#f97316","width":3},"thickness":0.75,"value":80}
            }
        ))
        fig_gauge.update_layout(**PLOTLY_LAYOUT, height=280)
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_bar:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Comparaison hebdomadaire — Planifié vs Réalisé")
        if not plan_m.empty:
            plan_sem = plan_m.groupby("Semaine_plan").size().reset_index(name="Planifié")
            plan_sem.columns = ["Semaine","Planifié"]
            if "Semaine" in jour_m.columns and not jour_m.empty:
                jour_sem = jour_m.groupby("Semaine").size().reset_index(name="Réalisé")
                compare  = plan_sem.merge(jour_sem, on="Semaine", how="left").fillna(0)
                compare["Réalisé"] = compare["Réalisé"].astype(int)
            else:
                compare = plan_sem.copy(); compare["Réalisé"] = 0
            compare["Semaine"] = compare["Semaine"].astype(str)
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name="Planifié", x=compare["Semaine"], y=compare["Planifié"], marker_color="#2563eb", opacity=0.85))
            fig_bar.add_trace(go.Bar(name="Réalisé",  x=compare["Semaine"], y=compare["Réalisé"],  marker_color="#16a34a", opacity=0.85))
            fig_bar.update_layout(**PLOTLY_LAYOUT, height=280, barmode="group",
                                   xaxis_title="Semaine", yaxis_title="Nb interventions")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Aucune donnée de planning pour ce mois.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── PAR SPÉCIALITÉ ──
    st.markdown("---")
    col_l2, col_r2 = st.columns(2, gap="large")

    with col_l2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Taux d'exécution par spécialité")
        if not plan_m.empty and "Spécialité" in plan_m.columns:
            plan_spec = plan_m.groupby("Spécialité").size().reset_index(name="Planifié")
            if "Spécialité" in jour_m.columns and not jour_m.empty:
                real_spec = jour_m.groupby("Spécialité").size().reset_index(name="Réalisé")
                spec_cmp  = plan_spec.merge(real_spec, on="Spécialité", how="left").fillna(0)
            else:
                spec_cmp = plan_spec.copy(); spec_cmp["Réalisé"] = 0
            spec_cmp["Taux (%)"] = (spec_cmp["Réalisé"] / spec_cmp["Planifié"] * 100).round(1)
            fig_spec = px.bar(spec_cmp, x="Spécialité", y=["Planifié","Réalisé"],
                              barmode="group", color_discrete_sequence=["#2563eb","#16a34a"])
            fig_spec.update_layout(**PLOTLY_LAYOUT, height=280)
            st.plotly_chart(fig_spec, use_container_width=True)
            st.dataframe(spec_cmp[["Spécialité","Planifié","Réalisé","Taux (%)"]].reset_index(drop=True),
                         use_container_width=True)
        else:
            st.info("Pas de données disponibles.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Répartition des interventions réalisées")
        if not jour_m.empty and "Categorie" in jour_m.columns:
            cat_r = jour_m["Categorie"].value_counts().reset_index()
            cat_r.columns = ["Catégorie","Total"]
            fig_cat = px.pie(cat_r, names="Catégorie", values="Total", hole=0.5,
                             color_discrete_sequence=["#f97316","#2563eb","#16a34a","#ca8a04","#dc2626"])
            fig_cat.update_layout(**PLOTLY_LAYOUT, height=280)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Aucune intervention réalisée sur cette période.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ONGLETS DÉTAIL ──
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📋 Tâches planifiées (TAG)", "✅ Interventions réalisées (Tag)", "📊 Synthèse équipements"])

    with tab1:
        st.caption(f"{len(plan_m)} tâche(s) planifiée(s) — colonne : TAG (planning)")
        st.dataframe(plan_m.sort_values("Date_plan").reset_index(drop=True), use_container_width=True, height=350)

    with tab2:
        # Affiche "Tag" (journal) tel quel
        cols_show = [c for c in ["Date","Tag","Equipement","Type d'opération","Spécialité","Statut opérationnel","Description"] if c in jour_m.columns]
        st.caption(f"{len(jour_m)} intervention(s) réalisée(s) — colonne : Tag (journal)")
        st.dataframe(jour_m[cols_show].sort_values("Date").reset_index(drop=True), use_container_width=True, height=350)

    with tab3:
        # Comparaison par équipement
        plan_eq = plan_m.groupby("Equipement").size().reset_index(name="Planifié") if not plan_m.empty else pd.DataFrame(columns=["Equipement","Planifié"])
        jour_eq = jour_m.groupby("Equipement").size().reset_index(name="Réalisé") if ("Equipement" in jour_m.columns and not jour_m.empty) else pd.DataFrame(columns=["Equipement","Réalisé"])
        compare_eq = plan_eq.merge(jour_eq, on="Equipement", how="outer").fillna(0)
        compare_eq["Planifié"] = compare_eq["Planifié"].astype(int)
        compare_eq["Réalisé"]  = compare_eq["Réalisé"].astype(int)
        compare_eq["Taux %"]   = (compare_eq["Réalisé"] / compare_eq["Planifié"].replace(0,1) * 100).round(1)
        compare_eq = compare_eq.sort_values("Taux %")
        st.dataframe(compare_eq.reset_index(drop=True), use_container_width=True, height=350)

    # ── EXPORT ──
    st.markdown("---")
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        if st.button("⬇ Exporter rapport d'exécution Excel", use_container_width=True):
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                plan_m.to_excel(writer, sheet_name="Planifié (TAG)",  index=False)
                jour_m.to_excel(writer, sheet_name="Réalisé (Tag)",   index=False)
                compare_eq.to_excel(writer, sheet_name="Synthèse",    index=False)
            mois_label = dt.date(2000, mois_s, 1).strftime("%B").capitalize()
            st.download_button("📥 Sauvegarder", buf.getvalue(),
                               file_name=f"suivi_execution_{mois_label}_{annee_s}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col_ex2:
        if st.button("Rapport PDF exécution", use_container_width=True):
            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=16, textColor=colors.HexColor("#f97316"))
            elements = []
            try: elements.append(RLImage("logo.png", width=3*cm, height=1.5*cm))
            except: pass
            elements.append(Spacer(1, 0.3*cm))
            mois_label = dt.date(2000, mois_s, 1).strftime("%B").capitalize()
            elements.append(Paragraph(f"RAPPORT D'EXÉCUTION — {mois_label} {annee_s}", title_style))
            elements.append(Paragraph(f"Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
            elements.append(Spacer(1, 0.5*cm))
            kpi_data = [["Indicateur","Valeur"],
                        ["Tâches planifiées",        str(nb_planifie)],
                        ["Interventions réalisées",  str(nb_realise)],
                        ["Taux d'exécution",         f"{taux_exec}%"],
                        ["Écart non réalisé",        str(nb_retard)],
                        ["Dont correctifs",          str(nb_correctif_m)]]
            tbl = Table(kpi_data, colWidths=[7*cm, 5*cm])
            tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#f97316")),
                ("TEXTCOLOR", (0,0),(-1,0), colors.white),
                ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
                ("GRID",      (0,0),(-1,-1), 0.5, colors.HexColor("#d1d5db")),
                ("ALIGN",     (1,0),(1,-1), "CENTER"),
                ("PADDING",   (0,0),(-1,-1), 8),
            ]))
            elements.append(tbl)
            elements.append(Spacer(1,0.5*cm))
            if not compare_eq.empty:
                elements.append(Paragraph("Synthèse par équipement", styles["Heading2"]))
                eq_rows = [["Equipement","Planifié","Réalisé","Taux %"]] + \
                          [[str(r["Equipement"]), str(r["Planifié"]), str(r["Réalisé"]), f"{r['Taux %']}%"]
                           for _, r in compare_eq.iterrows()]
                tbl2 = Table(eq_rows, repeatRows=1)
                tbl2.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#1a2332")),
                    ("TEXTCOLOR", (0,0),(-1,0), colors.HexColor("#f97316")),
                    ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
                    ("FONTSIZE",  (0,0),(-1,-1), 8),
                    ("GRID",      (0,0),(-1,-1), 0.4, colors.HexColor("#d1d5db")),
                    ("PADDING",   (0,0),(-1,-1), 5),
                ]))
                elements.append(tbl2)
            doc.build(elements)
            st.download_button("📥 Sauvegarder PDF", buf.getvalue(),
                               file_name=f"rapport_execution_{mois_label}_{annee_s}.pdf",
                               mime="application/pdf")
