import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION (TITRE ONGLET) ---
st.set_page_config(page_title="Outil Professeur - Trauma", page_icon="🏥", layout="wide")

# --- FICHIERS DE SAUVEGARDE ---
FILE_PATIENTS = "patients.csv"
FILE_FINANCE = "finances.csv"
FILE_STOCK = "stock.csv"

# --- INITIALISATION (Création des fichiers si absents) ---
def init_files():
    if not os.path.exists(FILE_PATIENTS):
        pd.DataFrame(columns=["Date", "IPP", "Nom", "Type_Accident", "Acte", "Chirurgien", "Paiement"]).to_csv(FILE_PATIENTS, index=False)
    if not os.path.exists(FILE_FINANCE):
        pd.DataFrame(columns=["Date", "Type", "Motif", "Montant"]).to_csv(FILE_FINANCE, index=False)
    if not os.path.exists(FILE_STOCK):
        pd.DataFrame({
            "Materiel": ["Clou Tibial", "Plaque Vissée", "Prothèse Hanche", "Vis Corticale", "Fil Suture"],
            "Stock": [10, 5, 2, 50, 100],
            "Seuil_Alerte": [3, 2, 1, 10, 20]
        }).to_csv(FILE_STOCK, index=False)

init_files()

# --- FONCTIONS DE CHARGEMENT ---
def load(file): return pd.read_csv(file)
def save(df, file): df.to_csv(file, index=False)

# --- INTERFACE ---
st.title("🏥 GESTION SERVICE TRAUMATOLOGIE")
st.markdown("### Outil de pilotage du Professeur")

# Menu de navigation
menu = st.radio("Menu", ["📊 TABLEAU DE BORD", "👨‍🤕 DOSSIERS PATIENTS", "💰 FINANCES", "📦 STOCK MATERIEL"], horizontal=True)
st.divider()

# --- 1. TABLEAU DE BORD ---
if menu == "📊 TABLEAU DE BORD":
    df_p = load(FILE_PATIENTS)
    df_f = load(FILE_FINANCE)
    df_s = load(FILE_STOCK)

    # Calculs
    recettes = df_f[df_f['Type']=="Recette"]['Montant'].sum()
    depenses = df_f[df_f['Type']=="Depense"]['Montant'].sum()
    stock_danger = len(df_s[df_s['Stock'] <= df_s['Seuil_Alerte']])

    # Affichage Indicateurs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Patients Enregistrés", len(df_p))
    c2.metric("Chiffre d'Affaires", f"{recettes:,.0f} GNF")
    c3.metric("Dépenses", f"{depenses:,.0f} GNF")
    c4.metric("Alertes Stock", stock_danger, delta="- Ruptures", delta_color="inverse")

    if stock_danger > 0:
        st.error(f"⚠️ ATTENTION : {stock_danger} articles sont en rupture de stock ! Voir onglet Stock.")

# --- 2. PATIENTS ---
elif menu == "👨‍🤕 DOSSIERS PATIENTS":
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("Nouvelle Admission")
        with st.form("form_patient"):
            nom = st.text_input("Nom Patient")
            ipp = st.text_input("IPP")
            acc = st.selectbox("Accident", ["AVP Moto", "AVP Auto", "Chute", "Autre"])
            acte = st.selectbox("Acte", ["Consultation", "Chirurgie", "Soins"])
            chir = st.selectbox("Chirurgien", ["Pr Samaké", "Assistant", "Interne"])
            paye = st.selectbox("Paiement", ["Réglé", "Impayé"])
            
            if st.form_submit_button("Enregistrer"):
                df = load(FILE_PATIENTS)
                new = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y"), ipp, nom, acc, acte, chir, paye]], columns=df.columns)
                save(pd.concat([df, new]), FILE_PATIENTS)
                st.success("Patient ajouté !")
                st.rerun()

    with c2:
        st.subheader("Liste des Patients")
        df = load(FILE_PATIENTS)
        st.dataframe(df, use_container_width=True)

# --- 3. FINANCES ---
elif menu == "💰 FINANCES":
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("Saisie Transaction")
        with st.form("form_finance"):
            type_f = st.selectbox("Type", ["Recette", "Depense"])
            motif = st.text_input("Motif (Ex: Cs M. Barry)")
            montant = st.number_input("Montant (GNF)", step=1000)
            
            if st.form_submit_button("Valider"):
                df = load(FILE_FINANCE)
                new = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y"), type_f, motif, montant]], columns=df.columns)
                save(pd.concat([df, new]), FILE_FINANCE)
                st.success("Enregistré !")
                st.rerun()
                
    with c2:
        st.subheader("Journal")
        df = load(FILE_FINANCE)
        st.dataframe(df, use_container_width=True)

# --- 4. STOCK ---
elif menu == "📦 STOCK MATERIEL":
    st.subheader("Inventaire Implants & Pharma")
    
    df = load(FILE_STOCK)
    
    # Éditeur de stock
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Sauvegarder les modifications de stock"):
        save(edited_df, FILE_STOCK)
        st.success("Stock mis à jour !")
        st.rerun()