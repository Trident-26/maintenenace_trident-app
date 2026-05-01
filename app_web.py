import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ML
from sklearn.ensemble import RandomForestRegressor
import joblib

# ===== CONFIG =====
st.set_page_config(page_title="Maintenance Systeme Trident", layout="wide")

# ===== LOGIN =====
if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("logo.png");
        background-size: cover;
        background-position: center;
    }
    .login-box {
        background: white;
        padding: 30px;
        border-radius: 12px;
        width: 350px;
        margin: auto;
        margin-top: 10%;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Maintenance Systeme")
    user = st.text_input("Utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Connexion"):
        if user == "admin" and password == "Trident@24":
            st.session_state["login"] = True
            st.rerun()
        else:
            st.error("Accès refusé")

    st.stop()

# ===== LOAD DATA =====
@st.cache_data
def load():
    df = pd.read_excel("journal.xlsx")
    df.columns = df.columns.str.strip()
    return df

df = load()
df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

# ===== CATEGORIE =====
def cat(x):
    if pd.isna(x): return "Autre"
    x = x.lower()
    if "correctif" in x: return "Correctif"
    if "préventif" in x: return "Préventif"
    if "signalement" in x: return "Signalement"
    if "surveil" in x: return "Surveillance"
    if "travaux" in x: return "Travaux"
    return "Autre"

df["Categorie"] = df["Type d'opération"].apply(cat)

# ===== SIDEBAR =====
st.sidebar.image("logo.png", width=140)
st.sidebar.markdown("## Systeme Maintenance Trident")

menu = st.sidebar.radio("Navigation", [
    "Dashboard","Journal","Equipes","Criticite","Predictif","Direction","Rapports"
])

# ===== FILTRES =====
st.sidebar.markdown("### Filtres")

date_range = st.sidebar.date_input("Période", [])
equipement = st.sidebar.multiselect("Equipement", df["Equipement"].dropna().unique())
tag = st.sidebar.multiselect("Tag", df["Tag"].dropna().unique())
specialite = st.sidebar.multiselect("Spécialité", df["Spécialité"].dropna().unique())

df_filtre = df.copy()

if len(date_range) == 2:
    df_filtre = df_filtre[
        (df_filtre["Date"] >= pd.to_datetime(date_range[0])) &
        (df_filtre["Date"] <= pd.to_datetime(date_range[1]))
    ]

if equipement:
    df_filtre = df_filtre[df_filtre["Equipement"].isin(equipement)]

if tag:
    df_filtre = df_filtre[df_filtre["Tag"].isin(tag)]

if specialite:
    df_filtre = df_filtre[df_filtre["Spécialité"].isin(specialite)]

# ===== KPI =====
def kpi(title, value):
    st.metric(title, value)

# ===== BASE =====
hs = df_filtre[df_filtre["Statut opérationnel"]=="HS"]
pannes = df_filtre[df_filtre["Categorie"]=="Correctif"]

total=len(df_filtre)
nb_hs=len(hs)
nb_pannes=len(pannes)
taux_dispo=((total-nb_hs)/total*100) if total else 0

# ================= DASHBOARD =================
if menu=="Dashboard":

    st.title("Tableau de bord Maintenance Trident-Ogx")

    c1,c2,c3,c4 = st.columns(4)

    with c1: kpi("Total opérations", total)
    with c2: kpi("Pannes", nb_pannes)
    with c3: kpi("HS", nb_hs)
    with c4: kpi("Disponibilité", f"{taux_dispo:.1f}%")

    st.subheader("Types d’opérations")
    st.bar_chart(df_filtre["Type d'opération"].value_counts())

    st.subheader("Charge par spécialité")
    st.bar_chart(df_filtre["Spécialité"].value_counts())

    st.subheader("Top équipements en panne")
    st.bar_chart(pannes["Tag"].value_counts().head(5))

# ================= JOURNAL =================
elif menu=="Journal":
    st.dataframe(df_filtre, use_container_width=True)

# ================= EQUIPES =================
elif menu=="Equipes":
    perf=pd.crosstab(df_filtre["Spécialité"],df_filtre["Type d'opération"])
    perf["Score"]=perf.get("Préventif",0)*2 - perf.get("Correctif",0)*2
    st.dataframe(perf)
    st.bar_chart(perf["Score"])

# ================= CRITICITE =================
elif menu=="Criticite":

    p=pannes.sort_values(["Tag","Date"])
    p["Intervalle"]=p.groupby("Tag")["Date"].diff().dt.days

    criticite=pd.DataFrame({
        "Pannes":p["Tag"].value_counts(),
        "MTBF":p.groupby("Tag")["Intervalle"].mean()
    }).fillna(0)

    st.dataframe(criticite)

# ================= PREDICTIF =================
elif menu=="Predictif":

    st.title("Maintenance Prédictive")

    p=pannes.sort_values(["Tag","Date"])
    p["Intervalle"]=p.groupby("Tag")["Date"].diff().dt.days

    last=p.groupby("Tag")["Date"].max()
    mtbf=p.groupby("Tag")["Intervalle"].mean()

    predict=pd.DataFrame({
        "Dernière panne":last,
        "MTBF":mtbf
    })

    predict["Dernière panne"]=pd.to_datetime(predict["Dernière panne"],errors='coerce')
    predict["MTBF"]=pd.to_numeric(predict["MTBF"],errors='coerce').fillna(0)

    predict=predict.dropna(subset=["Dernière panne"])

    predict["Prochaine panne"]=predict["Dernière panne"] + pd.to_timedelta(predict["MTBF"], unit='D')
    predict["Jours restants"]=(predict["Prochaine panne"]-pd.Timestamp.now()).dt.days

    # IA simple
    features=p.groupby("Tag").agg({
        "Intervalle":["mean","std"],
        "Date":"count"
    })
    features.columns=["MTBF","Var","Nb"]
    features=features.fillna(0)

    X=features
    y=features["MTBF"]

    try:
        model=joblib.load("model.pkl")
    except:
        model=RandomForestRegressor()

    model.fit(X,y)
    joblib.dump(model,"model.pkl")

    features["Prediction"]=model.predict(X)

    predict=predict.join(features["Prediction"], how="left")

    def priorite(x):
        if x<3:return "URGENT"
        elif x<7:return "CRITIQUE"
        elif x<15:return "PLANIFIER"
        else:return "NORMAL"

    predict["Priorité"]=predict["Prediction"].apply(priorite)

    st.dataframe(predict)
    st.bar_chart(predict["Priorité"].value_counts())

# ================= DIRECTION =================
elif menu=="Direction":

    st.title("Dashboard Direction")

    c1,c2,c3=st.columns(3)

    with c1: kpi("Disponibilité",f"{taux_dispo:.1f}%")
    with c2: kpi("Pannes",nb_pannes)
    with c3: kpi("HS",nb_hs)

    st.line_chart(pannes.groupby(pannes["Date"].dt.date).size())

# ================= RAPPORT =================
elif menu=="Rapports":

    st.title("Rapports")

    if st.button("Exporter Excel"):
        df_filtre.to_excel("rapport.xlsx", index=False)
        st.success("Export Excel OK")

    if st.button("Exporter PDF"):

        doc = SimpleDocTemplate("rapport.pdf")
        styles = getSampleStyleSheet()
        elements = []

        # ===== LOGO =====
        try:
            elements.append(Image("logo.png", width=120, height=60))
        except:
            pass

        elements.append(Spacer(1, 10))

        # ===== TITRE =====
        elements.append(Paragraph("RAPPORT DE MAINTENANCE", styles['Title']))
        elements.append(Spacer(1, 10))

        # ===== INFOS =====
        periode = (
            f"{date_range[0]} au {date_range[1]}"
            if len(date_range) == 2 else "Toutes les données"
        )

        elements.append(Paragraph(
            f"Période analysée : {periode}",
            styles['Normal']
        ))

        elements.append(Paragraph(
            f"Date de génération : {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles['Normal']
        ))

        elements.append(Spacer(1, 15))

        # ===== RECALCUL KPI SUR FILTRE =====
        hs_filtre = df_filtre[df_filtre["Statut opérationnel"]=="HS"]
        pannes_filtre = df_filtre[df_filtre["Categorie"]=="Correctif"]

        total_f = len(df_filtre)
        nb_hs_f = len(hs_filtre)
        nb_pannes_f = len(pannes_filtre)
        taux_dispo_f = ((total_f - nb_hs_f) / total_f * 100) if total_f else 0

        # ===== TABLE KPI =====
        data = [
            ["Indicateur", "Valeur"],
            ["Total opérations", total_f],
            ["Pannes", nb_pannes_f],
            ["Équipements HS", nb_hs_f],
            ["Disponibilité (%)", f"{taux_dispo_f:.1f}"]
        ]

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        # ===== SYNTHÈSE =====
        elements.append(Paragraph("1. Synthèse générale", styles['Heading2']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"Au cours de la période analysée, un total de {total_f} opérations de maintenance a été enregistré. "
            f"Parmi celles-ci, {nb_pannes_f} correspondent à des interventions correctives (pannes réelles). "
            f"{nb_hs_f} équipements sont actuellement hors service et nécessitent une intervention ou un suivi spécifique.",
            styles['Normal']
        ))

        elements.append(Spacer(1, 15))

        # ===== PERFORMANCE =====
        elements.append(Paragraph("2. Performance du système", styles['Heading2']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"Le taux de disponibilité global est estimé à {taux_dispo_f:.1f}%.",
            styles['Normal']
        ))

        if taux_dispo_f < 85:
            msg = "Ce niveau de performance est critique et nécessite des actions immédiates."
        elif taux_dispo_f < 95:
            msg = "Le système présente une performance moyenne avec possibilité d'amélioration."
        else:
            msg = "Le système présente une bonne performance opérationnelle."

        elements.append(Paragraph(msg, styles['Normal']))
        elements.append(Spacer(1, 15))

        # ===== TOP EQUIPEMENTS =====
        elements.append(Paragraph("3. Équipements les plus critiques", styles['Heading2']))
        elements.append(Spacer(1, 10))

        top_eq = pannes_filtre["Tag"].value_counts().head(3)

        for eq, val in top_eq.items():
            elements.append(Paragraph(f"- {eq} : {val} pannes", styles['Normal']))

        elements.append(Spacer(1, 15))

        # ===== RECOMMANDATIONS =====
        elements.append(Paragraph("4. Recommandations", styles['Heading2']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            "Il est recommandé de renforcer les actions de maintenance préventive sur les équipements critiques, "
            "d’optimiser la gestion des pièces de rechange et de réduire les délais d’intervention afin d’améliorer la disponibilité globale.",
            styles['Normal']
        ))

        elements.append(Spacer(1, 30))

        # ===== SIGNATURE =====
        elements.append(Paragraph("Responsable Maintenance", styles['Normal']))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("__________________________", styles['Normal']))

        # ===== BUILD =====
        doc.build(elements)

        st.success("Rapport PDF professionnel généré")