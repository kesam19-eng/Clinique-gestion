import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from PIL import Image
import base64
import io

# --- 1. CONFIGURATION (MODE HD & LARGE) ---
st.set_page_config(page_title="DONKA MANAGER ULTIMATE", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

# --- 2. DESIGN SYSTEM "HD PRINT" (LISIBILITÉ MAXIMALE) ---
st.markdown("""
    <style>
    /* TYPOGRAPHIE ET TAILLE */
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; font-size: 18px !important; color: #000000 !important; }
    
    /* FOND ET CONTRASTE */
    .stApp { background-color: #ffffff; }
    
    /* TITRES */
    h1 { color: #0d47a1 !important; font-size: 2.5rem !important; text-transform: uppercase; border-bottom: 2px solid #0d47a1; padding-bottom: 10px; }
    h2, h3 { color: #1565c0 !important; }
    
    /* CARTES KPIs */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa; border: 1px solid #ddd; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* BOUTONS TACTILES (GROS) */
    .stButton>button {
        height: 3.5em !important; font-size: 20px !important; border-radius: 8px !important;
        background-color: #0d47a1; color: white; border: none; width: 100%; margin-top: 10px;
    }
    
    /* TABLEAUX LISIBLES */
    .stDataFrame { font-size: 16px !important; }
    
    /* ONGLETS */
    .stTabs [data-baseweb="tab"] { font-size: 20px !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. FONCTIONS UTILITAIRES ---
def image_to_base64(image_file):
    """Convertit une image uploadée en texte pour la stocker dans la base"""
    if image_file is not None:
        try:
            bytes_data = image_file.getvalue()
            b64 = base64.b64encode(bytes_data).decode()
            return f"data:image/png;base64,{b64}"
        except: return None
    return None

# --- 4. INITIALISATION DES BASES DE DONNÉES ---
if 'patients' not in st.session_state:
    st.session_state.patients = pd.DataFrame(columns=[
        "IPP", "Nom", "Age", "Sexe", "Diagnostic", "Acte", "Chirurgien", 
        "Date_Entree", "Statut", "Evolution", "Complications", 
        "Image_Radio", "Rapport_CRO"
    ])

if 'finances' not in st.session_state:
    st.session_state.finances = pd.DataFrame(columns=["Date", "Type", "Categorie", "Description", "Montant"])

if 'stock' not in st.session_state:
    st.session_state.stock = pd.DataFrame([
        {"Item": "Clou Tibial", "Qte": 10, "Seuil": 5},
        {"Item": "Plaque LCP", "Qte": 3, "Seuil": 4},
        {"Item": "Vis Corticale", "Qte": 50, "Seuil": 20},
        {"Item": "Kit Champ Stérile", "Qte": 100, "Seuil": 15},
        {"Item": "Bétadine", "Qte": 12, "Seuil": 10},
    ])

# Raccourcis pour le code
df_pat = st.session_state.patients
df_fin = st.session_state.finances
df_stk = st.session_state.stock

# --- 5. NAVIGATION (SIDEBAR) ---
with st.sidebar:
    st.title("🏥 CHU DONKA")
    st.header("PR. LAMAH")
    st.info("Chef de Service\nTraumato-Orthopédie")
    st.write("---")
    menu = st.radio("MENU PRINCIPAL", 
        ["📊 VUE GLOBALE", 
         "👤 GESTION PATIENTS", 
         "✍️ RAPPORTS & PRINT", 
         "💰 COMPTABILITÉ", 
         "📦 STOCK & PHARMA", 
         "💾 EXPORT RECHERCHE"])
    st.write("---")
    if st.button("🔄 ACTUALISER"): st.rerun()

# ==============================================================================
# MODULE 1 : VUE GLOBALE (DASHBOARD)
# ==============================================================================
if menu == "📊 VUE GLOBALE":
    st.title("TABLEAU DE BORD")
    
    # CALCULS
    recettes = df_fin[df_fin['Type']=="Recette"]['Montant'].sum()
    depenses = df_fin[df_fin['Type']=="Dépense"]['Montant'].sum()
    solde = recettes - depenses
    actifs = len(df_pat[df_pat['Statut'].isin(['Hospitalisé', 'Bloc', 'Post-Op'])])
    alertes_stock = len(df_stk[df_stk['Qte'] <= df_stk['Seuil']])

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PATIENTS ACTIFS", actifs, "Lits occupés")
    c2.metric("SOLDE CAISSE", f"{solde:,.0f}", "GNF (Profit)")
    c3.metric("ALERTES STOCK", alertes_stock, "Articles critiques", delta_color="inverse")
    c4.metric("TOTAL DOSSIERS", len(df_pat), "Base Recherche")

    st.markdown("---")
    
    # STATS VISUELLES
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("📈 Activité Opératoire")
        if not df_pat.empty:
            fig = px.pie(df_pat, names='Acte', title="Répartition des Interventions", hole=0.4)
            fig.update_layout(font=dict(size=16))
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Aucune donnée.")
    
    with g2:
        st.subheader("⚠️ Complications (M&M)")
        if not df_pat.empty:
            df_comp = df_pat[df_pat['Complications'] != "RAS"]
            if not df_comp.empty:
                st.dataframe(df_comp[['Nom', 'Chirurgien', 'Complications']], use_container_width=True)
            else:
                st.success("Aucune complication active.")
        else: st.info("Aucune donnée.")

# ==============================================================================
# MODULE 2 : GESTION PATIENTS (ADMISSION + ÉVOLUTION + IMAGERIE)
# ==============================================================================
elif menu == "👤 GESTION PATIENTS":
    st.title("DOSSIERS CLINIQUES")
    
    tab1, tab2, tab3 = st.tabs(["📝 ADMISSION (NOUVEAU)", "🔍 SUIVI & ÉVOLUTION", "🩻 IMAGERIE & PREUVES"])
    
    # --- ONGLET 1 : ADMISSION ---
    with tab1:
        st.subheader("Entrée Nouveau Patient")
        with st.form("admission"):
            c1, c2 = st.columns(2)
            with c1:
                ipp = st.text_input("IPP (Numéro Dossier)")
                nom = st.text_input("Nom & Prénom")
                age = st.number_input("Âge", 0, 120, 30)
                sexe = st.radio("Sexe", ["M", "F"], horizontal=True)
                date_in = st.date_input("Date Entrée", datetime.now())
            with c2:
                diag = st.text_area("Diagnostic", height=100)
                acte = st.selectbox("Intervention", ["Enclouage", "Plaque Vissée", "Prothèse (PTH/PTG)", "Fixateur Externe", "Parage", "Autre"])
                chir = st.selectbox("Chirurgien", ["Pr Léopold Lamah", "Dr Senior", "Dr Samaké", "Autre"])
            
            if st.form_submit_button("✅ CRÉER LE DOSSIER"):
                if ipp and nom:
                    new = {
                        "IPP": ipp, "Nom": nom, "Age": age, "Sexe": sexe, "Diagnostic": diag, "Acte": acte, "Chirurgien": chir,
                        "Date_Entree": str(date_in), "Statut": "Hospitalisé", "Evolution": "J0: Admission.", "Complications": "RAS",
                        "Image_Radio": None, "Rapport_CRO": ""
                    }
                    st.session_state.patients = pd.concat([st.session_state.patients, pd.DataFrame([new])], ignore_index=True)
                    st.success("Patient enregistré.")
                else: st.error("Nom et IPP obligatoires.")

    # --- ONGLET 2 : SUIVI ---
    with tab2:
        if not df_pat.empty:
            sel = st.selectbox("Sélectionner Patient", df_pat['Nom'] + " (" + df_pat['IPP'] + ")", key="sel_suivi")
            ipp_sel = sel.split("(")[1].replace(")", "")
            idx = df_pat[df_pat['IPP'] == ipp_sel].index[0]
            p = df_pat.loc[idx]

            st.info(f"👤 **{p['Nom']}** | {p['Diagnostic']} | {p['Chirurgien']}")
            
            c_evo, c_stat = st.columns([2, 1])
            with c_evo:
                st.subheader("Journal d'Évolution")
                st.text_area("Historique", p['Evolution'], height=200, disabled=True)
                new_note = st.text_input("✍️ Note du jour (Ex: J3, Cicatrice OK)")
                if st.button("AJOUTER NOTE"):
                    ts = datetime.now().strftime("%d/%m")
                    st.session_state.patients.at[idx, 'Evolution'] += f"\n[{ts}] {new_note}"
                    st.success("Mise à jour effectuée.")
                    st.rerun()
            
            with c_stat:
                st.subheader("Statut & Alertes")
                curr_comp = p['Complications']
                new_comp = st.selectbox("Complication", ["RAS", "Infection", "Thrombose", "Choc", "Décès"], index=0 if curr_comp=="RAS" else 0)
                if new_comp != curr_comp and new_comp != "RAS":
                    st.session_state.patients.at[idx, 'Complications'] = new_comp
                    st.rerun()
                
                if curr_comp != "RAS": st.error(f"ALERTE : {curr_comp}")
                else: st.success("Pas de complication.")
                
                new_stat = st.selectbox("Position", ["Hospitalisé", "Bloc", "Sortie", "Consolidé"], index=0)
                if st.button("Changer Statut"):
                    st.session_state.patients.at[idx, 'Statut'] = new_stat
                    st.rerun()
        else: st.info("Aucun patient.")

    # --- ONGLET 3 : IMAGERIE (RESTORED) ---
    with tab3:
        if not df_pat.empty:
            sel_img = st.selectbox("Sélectionner Patient", df_pat['Nom'] + " (" + df_pat['IPP'] + ")", key="sel_img")
            ipp_img = sel_img.split("(")[1].replace(")", "")
            idx_img = df_pat[df_pat['IPP'] == ipp_img].index[0]
            
            c_in, c_view = st.columns(2)
            with c_in:
                st.write("**Ajouter une Radio/Preuve**")
                src = st.radio("Source", ["📸 Caméra", "📁 Fichier"], horizontal=True)
                img_data = None
                if src == "📸 Caméra":
                    img_cap = st.camera_input("Prendre photo")
                    if img_cap: img_data = img_cap
                else:
                    img_up = st.file_uploader("Choisir fichier", type=['png', 'jpg', 'jpeg'])
                    if img_up: img_data = img_up
                
                if img_data and st.button("ENREGISTRER IMAGE"):
                    b64 = image_to_base64(img_data)
                    st.session_state.patients.at[idx_img, 'Image_Radio'] = b64
                    st.success("Image archivée dans le dossier !")
                    st.rerun()
            
            with c_view:
                st.write("**Dernière Image du Dossier**")
                curr_img = df_pat.at[idx_img, 'Image_Radio']
                if curr_img:
                    st.image(curr_img, use_container_width=True)
                else:
                    st.info("Dossier sans image.")

# ==============================================================================
# MODULE 3 : RAPPORTS & PRINT (LE SECRÉTARIAT)
# ==============================================================================
elif menu == "✍️ RAPPORTS & PRINT":
    st.title("GÉNÉRATEUR DE RAPPORTS")
    
    if df_pat.empty:
        st.warning("Veuillez créer des patients d'abord.")
    else:
        sel_rep = st.selectbox("Choisir le Patient", df_pat['Nom'] + " (" + df_pat['IPP'] + ")", key="sel_rep")
        ipp_rep = sel_rep.split("(")[1].replace(")", "")
        p_rep = df_pat[df_pat['IPP'] == ipp_rep].iloc[0]
        
        st.subheader("Compte-Rendu Opératoire (CRO)")
        
        # Template automatique
        template = f"""CHU DE DONKA - TRAUMATOLOGIE ORTHOPÉDIE
SERVICE DU PR. LÉOPOLD LAMAH

COMPTE-RENDU OPÉRATOIRE
-----------------------
PATIENT : {p_rep['Nom']}
IPP : {p_rep['IPP']} | AGE : {p_rep['Age']} ans
DATE : {datetime.now().strftime('%d/%m/%Y')}
CHIRURGIEN : {p_rep['Chirurgien']}

DIAGNOSTIC : {p_rep['Diagnostic']}
INTERVENTION : {p_rep['Acte']}

DESCRIPTION DE L'ACTE :
Installation sur table orthopédique. Asepsie et champage usuels.
Incision voie classique. Dissection plan par plan.
Abord du foyer. Réduction satisfaisante.
Synthèse par {p_rep['Acte']}.
Contrôle scopique face/profil : OK.
Fermeture, Redon, Pansement compressif.

SUITES :
Surveillance constantes.
Antalgiques + HBPM.
Radio de contrôle à J1.

SIGNÉ :
{p_rep['Chirurgien']}
"""
        # Éditeur
        final_txt = st.text_area("Éditer le rapport avant impression", template, height=400)
        
        c_print, c_save = st.columns(2)
        with c_print:
            st.download_button("📥 TÉLÉCHARGER (POUR IMPRESSION WORD)", final_txt, file_name=f"CRO_{p_rep['IPP']}.txt")
            st.caption("Téléchargez le fichier, ouvrez-le, et imprimez (Ctrl+P).")
        
        with c_save:
            if st.button("💾 SAUVEGARDER DANS LE DOSSIER"):
                idx_rep = df_pat[df_pat['IPP'] == ipp_rep].index[0]
                st.session_state.patients.at[idx_rep, 'Rapport_CRO'] = final_txt
                st.success("Sauvegardé dans la base.")

# ==============================================================================
# MODULE 4 : COMPTABILITÉ
# ==============================================================================
elif menu == "💰 COMPTABILITÉ":
    st.title("FINANCES DU SERVICE")
    
    tab_mvt, tab_hist = st.tabs(["➕ ENREGISTRER MOUVEMENT", "📒 HISTORIQUE"])
    
    with tab_mvt:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Recette (Entrée)")
            with st.form("rec"):
                mt_r = st.number_input("Montant (GNF)", step=50000, key="mr")
                desc_r = st.text_input("Motif / Patient", key="dr")
                if st.form_submit_button("ENCAISSER"):
                    new = {"Date": str(datetime.now().date()), "Type": "Recette", "Categorie": "Patient", "Description": desc_r, "Montant": mt_r}
                    st.session_state.finances = pd.concat([st.session_state.finances, pd.DataFrame([new])], ignore_index=True)
                    st.success("Encaissé.")
        with c2:
            st.subheader("Dépense (Sortie)")
            with st.form("dep"):
                mt_d = st.number_input("Montant (GNF)", step=10000, key="md")
                cat_d = st.selectbox("Type", ["Matériel", "Pharmacie", "Primes", "Autre"])
                desc_d = st.text_input("Détail", key="dd")
                if st.form_submit_button("DÉCAISSER"):
                    new = {"Date": str(datetime.now().date()), "Type": "Dépense", "Categorie": cat_d, "Description": desc_d, "Montant": mt_d}
                    st.session_state.finances = pd.concat([st.session_state.finances, pd.DataFrame([new])], ignore_index=True)
                    st.warning("Dépense notée.")

    with tab_hist:
        if not df_fin.empty:
            st.dataframe(df_fin, use_container_width=True)
        else: st.info("Vide.")

# ==============================================================================
# MODULE 5 : STOCK
# ==============================================================================
elif menu == "📦 STOCK & PHARMA":
    st.title("GESTION MATÉRIEL")
    
    # Alertes rouges
    def highlight(row):
        return ['background-color: #ffcccc'] * len(row) if row.Qte <= row.Seuil else [''] * len(row)
    
    st.dataframe(df_stk.style.apply(highlight, axis=1), use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Mouvement Stock")
        item = st.selectbox("Article", df_stk['Item'])
        idx_s = df_stk[df_stk['Item'] == item].index[0]
        qty = st.number_input("Quantité", 1, 1000)
        
        ca, cb = st.columns(2)
        if ca.button("➖ SORTIE"): 
            st.session_state.stock.at[idx_s, 'Qte'] -= qty
            st.rerun()
        if cb.button("➕ ENTRÉE"):
            st.session_state.stock.at[idx_s, 'Qte'] += qty
            st.rerun()
            
    with c2:
        st.subheader("Nouveau Produit")
        with st.form("new_prod"):
            n = st.text_input("Nom")
            q = st.number_input("Qte Initiale", 0)
            s = st.number_input("Seuil Alerte", 5)
            if st.form_submit_button("AJOUTER"):
                st.session_state.stock = pd.concat([st.session_state.stock, pd.DataFrame([{"Item":n, "Qte":q, "Seuil":s}])], ignore_index=True)
                st.rerun()

# ==============================================================================
# MODULE 6 : EXPORT RECHERCHE
# ==============================================================================
elif menu == "💾 EXPORT RECHERCHE":
    st.title("EXTRACTION DE DONNÉES")
    st.write("Téléchargez les bases pour vos articles scientifiques (Excel / SPSS).")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Cohorte Patients")
        # On retire les images lourdes pour l'export Excel
        df_export = df_pat.drop(columns=['Image_Radio'])
        csv_pat = df_export.to_csv(index=False).encode('utf-8')
        st.download_button("📥 TÉLÉCHARGER (CSV)", csv_pat, "donka_patients.csv", "text/csv")
        st.caption("Contient : Clinique, Actes, Complications.")
        
    with c2:
        st.subheader("Journal Financier")
        csv_fin = df_fin.to_csv(index=False).encode('utf-8')
        st.download_button("📥 TÉLÉCHARGER (CSV)", csv_fin, "donka_finances.csv", "text/csv")
