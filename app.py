import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION (MODE LARGE) ---
st.set_page_config(page_title="DONKA MANAGER HD", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

# --- 🎨 DESIGN SYSTEM "HAUTE DÉFINITION" ---
st.markdown("""
    <style>
    /* 1. AUGMENTATION GLOBALE DE LA TAILLE DU TEXTE */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        font-size: 20px !important; /* Texte beaucoup plus gros */
    }
    
    /* 2. FOND ET COULEURS */
    .stApp {
        background-color: #f0f2f5; /* Gris très doux (Facebook style) */
        color: #1c1e21; /* Noir doux */
    }
    
    /* 3. CARTES (CARDS) - DESIGN MODERNE */
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #ddd;
    }
    
    /* 4. TITRES IMPOSANTS */
    h1 {
        color: #0d47a1 !important;
        font-size: 3rem !important;
        font-weight: 800 !important;
        text-transform: uppercase;
    }
    h2 {
        color: #1565c0 !important;
        font-size: 2.2rem !important;
        border-bottom: 2px solid #1565c0;
        padding-bottom: 10px;
    }
    h3 {
        font-size: 1.8rem !important;
        color: #424242 !important;
    }
    
    /* 5. BOUTONS TACTILES (GROS) */
    .stButton>button {
        height: 4em !important; /* Bouton très haut */
        font-size: 22px !important;
        border-radius: 12px !important;
        background-color: #0d47a1;
        color: white;
        border: none;
        box-shadow: 0 4px 0 #002171; /* Effet 3D */
        transition: all 0.2s;
    }
    .stButton>button:active {
        box-shadow: none;
        transform: translateY(4px);
    }
    
    /* 6. TABLEAUX LISIBLES */
    .stDataFrame {
        font-size: 18px !important;
    }
    
    /* 7. ALERTS ET MESSAGES */
    .stAlert {
        font-size: 20px !important;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION BASES ---
if 'patients' not in st.session_state:
    st.session_state.patients = pd.DataFrame(columns=["IPP", "Nom", "Age", "Diagnostic", "Acte", "Chirurgien", "Statut", "Evolution", "Complications"])
if 'finances' not in st.session_state:
    st.session_state.finances = pd.DataFrame(columns=["Date", "Type", "Categorie", "Montant"])
if 'stock' not in st.session_state:
    st.session_state.stock = pd.DataFrame([
        {"Item": "Clou Tibial", "Qte": 10, "Seuil": 5},
        {"Item": "Plaque LCP", "Qte": 3, "Seuil": 4},
        {"Item": "Vis Corticale", "Qte": 50, "Seuil": 20},
        {"Item": "Kit Champ", "Qte": 100, "Seuil": 15},
    ])

df_pat = st.session_state.patients
df_fin = st.session_state.finances
df_stk = st.session_state.stock

# --- SIDEBAR XXL ---
with st.sidebar:
    st.title("🏥 CHU DONKA")
    st.header("PR. LAMAH")
    st.write("---")
    # On utilise des gros emojis pour la lisibilité
    choix = st.radio("NAVIGATION", 
        ["📊 VUE GLOBALE", "👤 PATIENTS", "💰 COMPTABILITÉ", "📦 STOCK / PHARMA"],
        index=0)
    st.write("---")
    if st.button("🔄 ACTUALISER"):
        st.rerun()

# ==============================================================================
# 1. VUE GLOBALE (DASHBOARD HD)
# ==============================================================================
if choix == "📊 VUE GLOBALE":
    st.title("TABLEAU DE BORD")
    
    # KPIs en Cartes
    recettes = df_fin[df_fin['Type']=="Recette"]['Montant'].sum()
    actifs = len(df_pat[df_pat['Statut'].isin(['Hospitalisé', 'Bloc'])])
    alertes = len(df_stk[df_stk['Qte'] <= df_stk['Seuil']])

    c1, c2, c3 = st.columns(3)
    c1.metric("PATIENTS ACTIFS", f"{actifs}", "Hospitalisés ce jour")
    c2.metric("CHIFFRE D'AFFAIRES", f"{recettes:,.0f}", "Francs Guinéens (GNF)")
    c3.metric("ALERTES STOCK", f"{alertes}", "Commandes urgentes", delta_color="inverse")

    st.write("---")
    
    # Graphiques Larges
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("📈 Activité du Service")
        if not df_pat.empty:
            fig = px.pie(df_pat, names='Acte', title="Types d'interventions", hole=0.4)
            fig.update_layout(font=dict(size=18)) # Police graphique plus grosse
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Pas encore de patients.")
    
    with g2:
        st.subheader("📉 Finances (Entrées/Sorties)")
        if not df_fin.empty:
            fig2 = px.bar(df_fin, x='Type', y='Montant', color='Type', title="Flux Financier")
            fig2.update_layout(font=dict(size=18))
            st.plotly_chart(fig2, use_container_width=True)
        else: st.info("Pas encore de transactions.")

# ==============================================================================
# 2. PATIENTS (CARTE D'IDENTITÉ CLINIQUE)
# ==============================================================================
elif choix == "👤 PATIENTS":
    st.title("GESTION DES MALADES")
    
    tab1, tab2 = st.tabs(["📝 ADMISSION (NOUVEAU)", "🔍 SUIVI & ÉVOLUTION"])
    
    with tab1:
        st.subheader("Nouvelle Entrée")
        with st.form("new_pat"):
            c1, c2 = st.columns(2)
            with c1:
                ipp = st.text_input("NUMÉRO DOSSIER (IPP)")
                nom = st.text_input("NOM & PRÉNOM")
                diag = st.text_area("DIAGNOSTIC", height=100)
            with c2:
                acte = st.selectbox("INTERVENTION PRÉVUE", ["Enclouage", "Plaque Vissée", "Prothèse (PTH/PTG)", "Fixateur Externe", "Autre"])
                chir = st.selectbox("CHIRURGIEN", ["Pr Léopold Lamah", "Dr Senior", "Dr Samaké", "Autre"])
                statut = "Hospitalisé"
            
            if st.form_submit_button("✅ ENREGISTRER L'ADMISSION"):
                new = {"IPP": ipp, "Nom": nom, "Age": 0, "Diagnostic": diag, "Acte": acte, "Chirurgien": chir, "Statut": statut, "Evolution": "J0: Admission.", "Complications": "RAS"}
                st.session_state.patients = pd.concat([st.session_state.patients, pd.DataFrame([new])], ignore_index=True)
                st.success(f"Patient {nom} admis avec succès.")
    
    with tab2:
        st.subheader("Dossier Médical")
        if not df_pat.empty:
            sel = st.selectbox("SÉLECTIONNER UN PATIENT", df_pat['Nom'])
            idx = df_pat[df_pat['Nom'] == sel].index[0]
            p = df_pat.loc[idx]
            
            # Affichage style "Fiche"
            st.info(f"👤 **{p['Nom']}** | 🩺 {p['Diagnostic']} | 👨‍⚕️ {p['Chirurgien']}")
            
            c_evo, c_stat = st.columns([2, 1])
            with c_evo:
                st.markdown("### 📜 Évolution")
                # Affichage des notes précédentes (Lecture seule)
                st.text_area("Historique", p['Evolution'], height=200, disabled=True)
                
                # Ajout Note
                nouv_note = st.text_input("✍️ Ajouter une note du jour")
                if st.button("AJOUTER NOTE"):
                    timestamp = datetime.now().strftime("%d/%m")
                    st.session_state.patients.at[idx, 'Evolution'] += f"\n[{timestamp}] {nouv_note}"
                    st.success("Note ajoutée.")
                    st.rerun()
            
            with c_stat:
                st.markdown("### ⚠️ Alertes")
                # Complications
                curr_comp = p['Complications']
                new_comp = st.selectbox("Complication ?", ["RAS", "Infection", "Thrombose", "Choc"], index=0 if curr_comp=="RAS" else 0)
                if new_comp != curr_comp and new_comp != "RAS":
                    st.session_state.patients.at[idx, 'Complications'] = new_comp
                    st.error("Complication enregistrée !")
                
                if curr_comp != "RAS":
                    st.error(f"EN COURS : {curr_comp}")
                else:
                    st.success("État stable.")

# ==============================================================================
# 3. COMPTABILITÉ (CLAIRE & NETTE)
# ==============================================================================
elif choix == "💰 COMPTABILITÉ":
    st.title("FINANCES DU SERVICE")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("➕ Encaisser (Recette)")
        with st.form("recette"):
            montant_r = st.number_input("MONTANT (GNF)", step=50000)
            motif_r = st.text_input("MOTIF (Nom Patient)")
            if st.form_submit_button("VALIDER ENCAISSEMENT"):
                new_f = {"Date": str(datetime.now().date()), "Type": "Recette", "Categorie": "Patient", "Montant": montant_r}
                st.session_state.finances = pd.concat([st.session_state.finances, pd.DataFrame([new_f])], ignore_index=True)
                st.success("Caisse mise à jour.")
    
    with c2:
        st.subheader("➖ Dépenser (Sortie)")
        with st.form("depense"):
            montant_d = st.number_input("MONTANT (GNF)", step=10000)
            motif_d = st.selectbox("CATÉGORIE", ["Achat Matériel", "Pharmacie", "Primes", "Réparations", "Autre"])
            if st.form_submit_button("VALIDER DÉPENSE"):
                new_f = {"Date": str(datetime.now().date()), "Type": "Dépense", "Categorie": motif_d, "Montant": montant_d}
                st.session_state.finances = pd.concat([st.session_state.finances, pd.DataFrame([new_f])], ignore_index=True)
                st.warning("Dépense enregistrée.")

    st.write("---")
    st.subheader("📒 Journal des Opérations")
    if not df_fin.empty:
        st.dataframe(df_fin, use_container_width=True)

# ==============================================================================
# 4. STOCK (ALERTES VISUELLES)
# ==============================================================================
elif choix == "📦 STOCK / PHARMA":
    st.title("GESTION DU MATÉRIEL")
    
    # Affichage avec code couleur automatique
    st.write("Les lignes en **ROUGE** indiquent un stock critique.")
    
    def highlight_critical(row):
        if row.Qte <= row.Seuil:
            return ['background-color: #ffcccc; color: #990000; font-weight: bold'] * len(row)
        return [''] * len(row)

    st.dataframe(df_stk.style.apply(highlight_critical, axis=1), use_container_width=True)
    
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Mise à jour Stock")
        item = st.selectbox("Article", df_stk['Item'])
        idx_s = df_stk[df_stk['Item'] == item].index[0]
        qty = st.number_input("Quantité", 1, 100)
        
        col_a, col_b = st.columns(2)
        if col_a.button("➖ SORTIR (UTILISÉ)"):
            st.session_state.stock.at[idx_s, 'Qte'] -= qty
            st.rerun()
        if col_b.button("➕ ENTRER (LIVRÉ)"):
            st.session_state.stock.at[idx_s, 'Qte'] += qty
            st.rerun()

    with c2:
        st.info("ℹ️ Pour ajouter un nouvel article (ex: Prothèse), utilisez le bouton ci-dessous.")
        with st.expander("Créer nouvel article"):
            n_item = st.text_input("Nom")
            n_qte = st.number_input("Stock départ", 0)
            n_seuil = st.number_input("Seuil alerte", 5)
            if st.button("CRÉER"):
                new_s = {"Item": n_item, "Qte": n_qte, "Seuil": n_seuil}
                st.session_state.stock = pd.concat([st.session_state.stock, pd.DataFrame([new_s])], ignore_index=True)
                st.rerun()
