import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from PIL import Image
import base64
import io
import time

# --- 1. CONFIGURATION INITIALE ---
st.set_page_config(page_title="DONKA MANAGER SECURE", page_icon="🔒", layout="wide", initial_sidebar_state="collapsed")

# --- 2. GESTION DE LA SÉCURITÉ (LOGIN SYSTEM) ---

# Initialisation de l'état de connexion
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    """Vérifie le mot de passe"""
    # ==========================================
    # 🔑 LE MOT DE PASSE EST ICI (Change-le !)
    # ==========================================
    SECRET_PASSWORD = "DONKA2025" 
    
    if st.session_state.password_input == SECRET_PASSWORD:
        st.session_state.authenticated = True
        del st.session_state.password_input # On efface le mdp de la mémoire pour sécurité
    else:
        st.error("⛔ Mot de passe incorrect")

# --- ÉCRAN DE CONNEXION (Si pas connecté) ---
if not st.session_state.authenticated:
    st.markdown("""
        <style>
        .stApp {background-color: #0d47a1;} /* Fond Bleu Donka */
        .login-box {
            background-color: white; padding: 40px; border-radius: 15px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center;
            max-width: 500px; margin: 100px auto;
        }
        h1 {color: #0d47a1; font-family: 'Segoe UI', sans-serif;}
        .stTextInput>div>div>input {text-align: center; font-size: 20px;}
        .stButton>button {width: 100%; background-color: #0d47a1; color: white; height: 3em; font-size: 18px;}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="login-box">
            <h1>🏥 CHU DONKA</h1>
            <h3>TRAUMATO-ORTHOPÉDIE</h3>
            <p>Espace Numérique Sécurisé - Pr. LAMAH</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.text_input("🔒 Entrez le Code d'Accès", type="password", key="password_input", on_change=check_password)
        if st.button("SE CONNECTER"):
            check_password()
            
    st.stop() # 🛑 ARRÊTE TOUT ICI SI PAS CONNECTÉ

# ==============================================================================
# 🟢 DÉBUT DE L'APPLICATION (VISIBLE SEULEMENT SI CONNECTÉ)
# ==============================================================================

# --- STYLE VISUEL (MODE HD) ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; font-size: 18px !important; color: #000000 !important; }
    .stApp { background-color: #ffffff; }
    h1 { color: #0d47a1 !important; font-size: 2.5rem !important; text-transform: uppercase; border-bottom: 2px solid #0d47a1; padding-bottom: 10px; }
    h2, h3 { color: #1565c0 !important; }
    div[data-testid="metric-container"] { background-color: #f8f9fa; border: 1px solid #ddd; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .stButton>button { height: 3.5em !important; font-size: 20px !important; border-radius: 8px !important; background-color: #0d47a1; color: white; border: none; width: 100%; margin-top: 10px; }
    .stDataFrame { font-size: 16px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 20px !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- FONCTIONS ---
def image_to_base64(image_file):
    if image_file is not None:
        try:
            bytes_data = image_file.getvalue()
            b64 = base64.b64encode(bytes_data).decode()
            return f"data:image/png;base64,{b64}"
        except: return None
    return None

# --- BASES DE DONNÉES ---
if 'patients' not in st.session_state:
    st.session_state.patients = pd.DataFrame(columns=["IPP", "Nom", "Age", "Sexe", "Diagnostic", "Acte", "Chirurgien", "Date_Entree", "Statut", "Evolution", "Complications", "Image_Radio", "Rapport_CRO"])
if 'finances' not in st.session_state:
    st.session_state.finances = pd.DataFrame(columns=["Date", "Type", "Categorie", "Description", "Montant"])
if 'stock' not in st.session_state:
    st.session_state.stock = pd.DataFrame([{"Item": "Clou Tibial", "Qte": 10, "Seuil": 5}, {"Item": "Plaque LCP", "Qte": 3, "Seuil": 4}, {"Item": "Vis Corticale", "Qte": 50, "Seuil": 20}, {"Item": "Kit Champ Stérile", "Qte": 100, "Seuil": 15}, {"Item": "Bétadine", "Qte": 12, "Seuil": 10}])

df_pat = st.session_state.patients
df_fin = st.session_state.finances
df_stk = st.session_state.stock

# --- SIDEBAR (NAVIGATION) ---
with st.sidebar:
    st.title("🏥 CHU DONKA")
    st.caption("Connecté en tant que Pr. LAMAH")
    st.write("---")
    menu = st.radio("MENU", ["📊 VUE GLOBALE", "👤 GESTION PATIENTS", "✍️ RAPPORTS & PRINT", "💰 COMPTABILITÉ", "📦 STOCK & PHARMA", "💾 EXPORT RECHERCHE"])
    st.write("---")
    if st.button("🔒 DÉCONNEXION"):
        st.session_state.authenticated = False
        st.rerun()

# --- MODULES DE L'APP ---

# 1. VUE GLOBALE
if menu == "📊 VUE GLOBALE":
    st.title("TABLEAU DE BORD")
    rec = df_fin[df_fin['Type']=="Recette"]['Montant'].sum()
    dep = df_fin[df_fin['Type']=="Dépense"]['Montant'].sum()
    act = len(df_pat[df_pat['Statut'].isin(['Hospitalisé', 'Bloc', 'Post-Op'])])
    alt = len(df_stk[df_stk['Qte'] <= df_stk['Seuil']])
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PATIENTS ACTIFS", act, "Lits occupés")
    c2.metric("SOLDE CAISSE", f"{rec-dep:,.0f}", "GNF")
    c3.metric("ALERTES STOCK", alt, "Critiques", delta_color="inverse")
    c4.metric("TOTAL DOSSIERS", len(df_pat), "Base")
    
    st.markdown("---")
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Activité")
        if not df_pat.empty:
            st.plotly_chart(px.pie(df_pat, names='Acte', hole=0.4), use_container_width=True)
        else: st.info("Aucune donnée")
    with g2:
        st.subheader("Complications Actives")
        if not df_pat.empty:
            comp = df_pat[df_pat['Complications'] != "RAS"]
            if not comp.empty: st.dataframe(comp[['Nom', 'Complications']], use_container_width=True)
            else: st.success("RAS")

# 2. PATIENTS
elif menu == "👤 GESTION PATIENTS":
    st.title("DOSSIERS CLINIQUES")
    t1, t2, t3 = st.tabs(["ADMISSION", "SUIVI", "IMAGERIE"])
    
    with t1:
        with st.form("adm"):
            c1, c2 = st.columns(2)
            with c1:
                ipp = st.text_input("IPP")
                nom = st.text_input("Nom")
                age = st.number_input("Age", 0, 120, 30)
                sexe = st.radio("Sexe", ["M","F"], horizontal=True)
            with c2:
                diag = st.text_area("Diag")
                acte = st.selectbox("Acte", ["Enclouage", "Plaque", "Prothèse", "Fixateur", "Autre"])
                chir = st.selectbox("Chirurgien", ["Pr Lamah", "Dr Senior", "Dr Samaké", "Autre"])
            if st.form_submit_button("ENREGISTRER") and ipp:
                new = {"IPP": ipp, "Nom": nom, "Age": age, "Sexe": sexe, "Diagnostic": diag, "Acte": acte, "Chirurgien": chir, "Date_Entree": str(datetime.now().date()), "Statut": "Hospitalisé", "Evolution": "J0: Entrée.", "Complications": "RAS", "Image_Radio": None, "Rapport_CRO": ""}
                st.session_state.patients = pd.concat([st.session_state.patients, pd.DataFrame([new])], ignore_index=True)
                st.success("OK")
    
    with t2:
        if not df_pat.empty:
            sel = st.selectbox("Patient", df_pat['Nom'] + " (" + df_pat['IPP'] + ")")
            idx = df_pat[df_pat['IPP'] == sel.split("(")[1][:-1]].index[0]
            p = df_pat.loc[idx]
            st.info(f"{p['Nom']} | {p['Diagnostic']}")
            c1, c2 = st.columns([2,1])
            with c1:
                st.text_area("Histo", p['Evolution'], height=200, disabled=True)
                n = st.text_input("Note")
                if st.button("AJOUTER") and n:
                    st.session_state.patients.at[idx, 'Evolution'] += f"\n[{datetime.now().strftime('%d/%m')}] {n}"
                    st.rerun()
            with c2:
                comp = st.selectbox("Complication", ["RAS", "Infection", "Thrombose", "Choc"], index=0 if p['Complications']=="RAS" else 0)
                if comp != p['Complications']:
                    st.session_state.patients.at[idx, 'Complications'] = comp
                    st.rerun()
                if comp != "RAS": st.error(comp)
    
    with t3:
        if not df_pat.empty:
            sel = st.selectbox("Patient Image", df_pat['Nom'] + " (" + df_pat['IPP'] + ")", key="img_sel")
            idx = df_pat[df_pat['IPP'] == sel.split("(")[1][:-1]].index[0]
            src = st.radio("Source", ["Caméra", "Fichier"], horizontal
