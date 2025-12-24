import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from PIL import Image
import base64
import io
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="DONKA MANAGER DEMO", page_icon="🏥", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SÉCURITÉ ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    SECRET = "DONKA2025" 
    if st.session_state.pwd == SECRET:
        st.session_state.authenticated = True
        del st.session_state.pwd
    else: st.error("Code Erroné")

if not st.session_state.authenticated:
    st.markdown("""<style>.stApp {background-color:#0d47a1; color:white} .box{background:white;padding:30px;border-radius:10px;text-align:center;color:black;margin-top:50px}</style>""", unsafe_allow_html=True)
    st.markdown("<div class='box'><h1>🏥 CHU DONKA</h1><h3>ACCÈS SÉCURISÉ</h3></div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        st.text_input("CODE D'ACCÈS", type="password", key="pwd", on_change=check_password)
        st.button("ENTRER", on_click=check_password)
    st.stop()

# --- 3. STYLE HD ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; font-size: 18px !important; color: #000 !important; }
    .stApp { background-color: #ffffff; }
    h1 { color: #0d47a1 !important; font-size: 2.2rem !important; border-bottom: 2px solid #0d47a1; text-transform:uppercase;}
    h2, h3 { color: #1565c0 !important; }
    .stButton>button { height: 3.5em !important; font-size: 20px !important; background-color: #0d47a1; color: white; width: 100%; border-radius: 8px;}
    div[data-testid="metric-container"] { background-color: #f0f2f6; border: 1px solid #ccc; padding: 15px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. FONCTIONS & DONNÉES (AVEC PATIENT DÉMO !!) ---
def img_to_b64(file):
    try: return f"data:image/png;base64,{base64.b64encode(file.getvalue()).decode()}"
    except: return None

# ICI : J'AJOUTE LE PATIENT FICTIF POUR QUE L'APPLI NE SOIT PAS VIDE
if 'patients' not in st.session_state:
    cols = ["IPP", "Nom", "Age", "Sexe", "Diagnostic", "Acte", "Chirurgien", "Date_Entree", "Statut", "Evolution", "Complications", "Image_Radio", "Rapport_CRO"]
    # Patient Exemple pré-rempli
    demo = pd.DataFrame([
        ["T-100", "M. DIALLO Alpha", 45, "M", "Fr. Ouverte Tibia D", "Enclouage CM", "Pr Lamah", 
         str(datetime.now().date()), "Hospitalisé", "J0: Admission Urgences.\nJ1: Bloc Opératoire OK.", "RAS", None, ""]
    ], columns=cols)
    st.session_state.patients = demo

if 'finances' not in st.session_state:
    st.session_state.finances = pd.DataFrame([["2023-12-24", "Recette", "Patient", "Diallo A.", 5000000]], columns=["Date", "Type", "Categorie", "Description", "Montant"])

if 'stock' not in st.session_state:
    st.session_state.stock = pd.DataFrame([{"Item": "Clou Tibial", "Qte": 10, "Seuil": 5}, {"Item": "Plaque LCP", "Qte": 2, "Seuil": 4}, {"Item": "Vis", "Qte": 50, "Seuil": 20}])

# Raccourcis
df_pat = st.session_state.patients
df_fin = st.session_state.finances
df_stk = st.session_state.stock

# --- 5. NAVIGATION ---
with st.sidebar:
    st.title("🏥 DONKA MANAGER")
    st.info("Pr. LÉOPOLD LAMAH")
    menu = st.radio("MENU", ["📊 VUE GLOBALE", "👤 DOSSIERS PATIENTS", "✍️ RAPPORTS", "💰 FINANCES", "📦 STOCK", "💾 EXPORT"])
    if st.button("🔒 QUITTER"):
        st.session_state.authenticated = False
        st.rerun()

# --- MODULES ---

if menu == "📊 VUE GLOBALE":
    st.title("TABLEAU DE BORD")
    rec = df_fin[df_fin['Type']=="Recette"]['Montant'].sum()
    act = len(df_pat[df_pat['Statut'].isin(['Hospitalisé','Bloc'])])
    alt = len(df_stk[df_stk['Qte'] <= df_stk['Seuil']])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("LITS OCCUPÉS", act)
    c2.metric("CAISSE (GNF)", f"{rec:,.0f}")
    c3.metric("ALERTES STOCK", alt, delta_color="inverse")
    
    st.markdown("---")
    g1, g2 = st.columns(2)
    with g1: 
        st.subheader("Activité")
        st.plotly_chart(px.pie(df_pat, names='Acte', hole=0.4), use_container_width=True)
    with g2:
        st.subheader("État Clinique")
        st.write("Patients Hospitalisés :")
        st.dataframe(df_pat[['Nom', 'Diagnostic', 'Statut']], use_container_width=True)

elif menu == "👤 DOSSIERS PATIENTS":
    st.title("SUIVI CLINIQUE")
    t1, t2, t3 = st.tabs(["ADMISSION", "SUIVI & ÉVOLUTION", "IMAGERIE"])
    
    with t1:
        with st.form("new"):
            c1, c2 = st.columns(2)
            with c1:
                ipp = st.text_input("IPP")
                nom = st.text_input("Nom")
                age = st.number_input("Age",0)
                sexe = st.radio("Sexe", ["M","F"], horizontal=True)
            with c2:
                diag = st.text_area("Diag")
                acte = st.selectbox("Acte", ["Enclouage", "Plaque", "Fixateur", "Autre"])
                chir = st.selectbox("Chir", ["Pr Lamah", "Dr Senior", "Dr Samaké"])
            if st.form_submit_button("CRÉER DOSSIER") and ipp:
                new = {"IPP": ipp, "Nom": nom, "Age": age, "Sexe": sexe, "Diagnostic": diag, "Acte": acte, "Chirurgien": chir, "Date_Entree": str(datetime.now().date()), "Statut": "Hospitalisé", "Evolution": "J0: Entrée.", "Complications": "RAS", "Image_Radio": None, "Rapport_CRO": ""}
                st.session_state.patients = pd.concat([st.session_state.patients, pd.DataFrame([new])], ignore_index=True)
                st.success("OK")

    with t2:
        # SÉLECTEUR DE PATIENT (C'est ça qui était vide avant !)
        if not df_pat.empty:
            p_list = df_pat['Nom'] + " (" + df_pat['IPP'] + ")"
            sel = st.selectbox("🔍 SÉLECTIONNER UN PATIENT", p_list)
            ipp_sel = sel.split("(")[1][:-1]
            idx = df_pat[df_pat['IPP'] == ipp_sel].index[0]
            p = df_pat.loc[idx]
            
            st.info(f"**{p['Nom']}** | {p['Diagnostic']} | {p['Statut']}")
            
            c_evo, c_alert = st.columns([2,1])
            with c_evo:
                st.subheader("Journal")
                st.text_area("Historique", p['Evolution'], height=200, disabled=True)
                note = st.text_input("Nouvelle note (ex: J2, Redon ablaté)")
                if st.button("AJOUTER NOTE"):
                    st.session_state.patients.at[idx, 'Evolution'] += f"\n[{datetime.now().strftime('%d/%m')}] {note}"
                    st.rerun()
            with c_alert:
                st.subheader("Alerte")
                comp = st.selectbox("Complication", ["RAS", "Infection", "Choc"], index=0 if p['Complications']=="RAS" else 0)
                if comp != p['Complications']:
                    st.session_state.patients.at[idx, 'Complications'] = comp
                    st.rerun()
                if comp != "RAS": st.error(comp)
        else:
            st.warning("Aucun patient dans la base.")

    with t3:
        # IMAGERIE
        if not df_pat.empty:
            # On réutilise la sélection faite en T2 ou on refait un selectbox
            sel_img = st.selectbox("Patient pour Image", df_pat['Nom'] + " (" + df_pat['IPP'] + ")", key="sel_img")
            ipp_img = sel_img.split("(")[1][:-1]
            idx_img = df_pat[df_pat['IPP'] == ipp_img].index[0]
            
            c_cam, c_view = st.columns(2)
            with c_cam:
                src = st.radio("Source", ["Caméra", "Fichier"], horizontal=True)
                if src == "Caméra":
                    img = st.camera_input("Photo Radio")
                else:
                    img = st.file_uploader("Upload")
                
                if img and st.button("ENREGISTRER PREUVE"):
                    st.session_state.patients.at[idx_img, 'Image_Radio'] = img_to_b64(img)
                    st.success("Sauvegardé !")
                    st.rerun()
            with c_view:
                curr = df_pat.at[idx_img, 'Image_Radio']
                if curr: st.image(curr, caption="Dernière Imagerie")
                else: st.info("Pas d'image.")

elif menu == "✍️ RAPPORTS":
    st.title("RAPPORTS MÉDICAUX")
    if not df_pat.empty:
        sel = st.selectbox("Patient", df_pat['Nom'])
        idx = df_pat[df_pat['Nom']==sel].index[0]
        p = df_pat.loc[idx]
        txt = st.text_area("Éditeur CRO", f"CHU DONKA\nCRO: {p['Nom']}\nACTE: {p['Acte']}\n\nL'intervention s'est déroulée...", height=300)
        st.download_button("TÉLÉCHARGER TXT", txt, f"CRO_{p['IPP']}.txt")

elif menu == "💰 FINANCES":
    st.title("COMPTABILITÉ")
    c1, c2 = st.columns(2)
    with c1:
        m = st.number_input("Recette (+)", step=50000)
        if st.button("ENCAISSER"):
            st.session_state.finances = pd.concat([st.session_state.finances, pd.DataFrame([{"Date":str(datetime.now().date()), "Type":"Recette", "Categorie":"Patient", "Description":"-", "Montant":m}])], ignore_index=True)
            st.success("OK")
    with c2:
        if not df_fin.empty: st.dataframe(df_fin)

elif menu == "📦 STOCK":
    st.title("STOCK")
    st.dataframe(df_stk.style.apply(lambda x: ['background-color:#ffcccc']*len(x) if x.Qte<=x.Seuil else ['']*len(x), axis=1), use_container_width=True)

elif menu == "💾 EXPORT":
    st.title("RECHERCHE")
    st.download_button("CSV PATIENTS", df_pat.drop(columns=['Image_Radio']).to_csv().encode('utf-8'), "pat.csv")
