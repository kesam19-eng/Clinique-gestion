    import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="DONKA INTEGRAL MANAGER", page_icon="🏥", layout="wide")

# --- STYLE PRO & ALERTE ---
st.markdown("""
    <style>
    .stApp {background-color: #f4f6f9;}
    .metric-box {background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;}
    .big-num {font-size: 24px; font-weight: bold; color: #2c3e50;}
    .label {font-size: 14px; color: #7f8c8d; text-transform: uppercase;}
    /* Couleurs Status */
    .success {color: #27ae60;}
    .danger {color: #c0392b;}
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION BASES DE DONNÉES ---
if 'patients' not in st.session_state:
    st.session_state.patients = pd.DataFrame(columns=[
        "IPP", "Date_Entree", "Nom", "Age", "Sexe", "Diagnostic", "Acte", "Chirurgien", 
        "Statut", "Evolution_Notes", "Complications"
    ])

if 'finances' not in st.session_state:
    # Type: Recette ou Dépense
    st.session_state.finances = pd.DataFrame(columns=["Date", "Type", "Categorie", "Description", "Montant"])

if 'stock' not in st.session_state:
    # Stock initial simulé
    st.session_state.stock = pd.DataFrame([
        {"Item": "Clou Tibial", "Qte": 10, "Seuil": 5},
        {"Item": "Plaque LCP 4.5", "Qte": 4, "Seuil": 5},
        {"Item": "Vis Corticale", "Qte": 50, "Seuil": 20},
        {"Item": "Kit Champ Stérile", "Qte": 100, "Seuil": 15},
        {"Item": "Bétadine 500ml", "Qte": 12, "Seuil": 10},
    ])

# Raccourcis
df_pat = st.session_state.patients
df_fin = st.session_state.finances
df_stk = st.session_state.stock

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏥 DONKA MANAGER")
    st.caption("Système Intégral v5.0")
    menu = st.radio("Navigation", 
                    ["📊 VUE D'ENSEMBLE", 
                     "👤 DOSSIERS & ÉVOLUTION", 
                     "💰 FINANCE COMPLÈTE", 
                     "📦 GESTION STOCKS", 
                     "💾 SAUVEGARDE"])

# ==============================================================================
# 1. VUE D'ENSEMBLE (Dashboard Hybride)
# ==============================================================================
if menu == "📊 VUE D'ENSEMBLE":
    st.title("Tableau de Bord Direction")
    
    # CALCULS FINANCIERS
    recettes = df_fin[df_fin['Type'] == "Recette"]['Montant'].sum()
    depenses = df_fin[df_fin['Type'] == "Dépense"]['Montant'].sum()
    solde = recettes - depenses
    
    # CALCULS MEDICAUX
    actifs = len(df_pat[df_pat['Statut'].isin(['Hospitalisé', 'Post-Op'])])
    compliques = len(df_pat[df_pat['Complications'] != 'RAS']) if not df_pat.empty else 0

    # AFFICHAGE KPI
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-box'><div class='label'>Patients Actifs</div><div class='big-num'>{actifs}</div></div>", unsafe_allow_html=True)
    with c2: 
        color = "danger" if compliques > 0 else "success"
        st.markdown(f"<div class='metric-box'><div class='label'>Complications</div><div class='big-num {color}'>{compliques}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-box'><div class='label'>Recettes Totales</div><div class='big-num success'>+{recettes:,.0f}</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-box'><div class='label'>Solde (Profit)</div><div class='big-num'>{solde:,.0f} GNF</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Flux Financier")
        if not df_fin.empty:
            fig_fin = px.pie(df_fin, names='Type', values='Montant', title="Recettes vs Dépenses", hole=0.5, color_discrete_map={"Recette":"#2ecc71", "Dépense":"#e74c3c"})
            st.plotly_chart(fig_fin, use_container_width=True)
        else: st.info("Aucune donnée financière.")
        
    with g2:
        st.subheader("Activité Chirurgicale")
        if not df_pat.empty:
            fig_act = px.bar(df_pat, x='Acte', title="Interventions Réalisées")
            st.plotly_chart(fig_act, use_container_width=True)
        else: st.info("Aucun patient enregistré.")

# ==============================================================================
# 2. DOSSIERS & ÉVOLUTION (Le Cœur Médical)
# ==============================================================================
elif menu == "👤 DOSSIERS & ÉVOLUTION":
    st.title("Suivi Clinique Avancé")
    
    tab1, tab2 = st.tabs(["📝 Nouvelle Admission", "🔍 Suivi & Évolution"])
    
    # --- AJOUT PATIENT ---
    with tab1:
        with st.form("new_pat"):
            c1, c2 = st.columns(2)
            with c1:
                ipp = st.text_input("IPP")
                nom = st.text_input("Nom")
                diag = st.text_area("Diagnostic")
            with c2:
                acte = st.selectbox("Acte", ["Enclouage", "Plaque", "Prothèse", "Fixateur", "Autre"])
                chir = st.selectbox("Chirurgien", ["Pr Lamah", "Dr Senior", "Dr Samaké", "Autre"])
                statut = "Hospitalisé"
            
            if st.form_submit_button("Admettre Patient"):
                new = {
                    "IPP": ipp, "Date_Entree": str(datetime.now().date()), "Nom": nom, 
                    "Age": 0, "Sexe": "M", "Diagnostic": diag, "Acte": acte, 
                    "Chirurgien": chir, "Statut": statut, 
                    "Evolution_Notes": f"{datetime.now().strftime('%d/%m')}: Admission au service.",
                    "Complications": "RAS"
                }
                st.session_state.patients = pd.concat([st.session_state.patients, pd.DataFrame([new])], ignore_index=True)
                st.success("Patient admis.")

    # --- SUIVI ÉVOLUTIF (La nouveauté) ---
    with tab2:
        if df_pat.empty:
            st.warning("Base vide.")
        else:
            pat_list = df_pat['IPP'] + " - " + df_pat['Nom']
            sel_pat = st.selectbox("Choisir un patient pour le suivi", pat_list)
            idx = df_pat[df_pat['IPP'] == sel_pat.split(" - ")[0]].index[0]
            
            # Affichage Données Actuelles
            p = df_pat.loc[idx]
            st.info(f"**Patient :** {p['Nom']} | **Diag:** {p['Diagnostic']} | **Statut:** {p['Statut']}")
            
            col_evo, col_act = st.columns([2, 1])
            
            with col_evo:
                st.subheader("📜 Historique d'Évolution")
                # Zone de lecture seule des notes précédentes
                st.text_area("Journal Clinique", p['Evolution_Notes'], height=200, disabled=True)
                
                # Ajout nouvelle note
                new_note = st.text_input("➕ Ajouter une note du jour (Ex: J3, ablation redon, T°37)")
                if st.button("Ajouter au Journal"):
                    timestamp = datetime.now().strftime("%d/%m %Hh")
                    entry = f"\n[{timestamp}] {new_note}"
                    st.session_state.patients.at[idx, 'Evolution_Notes'] += entry
                    st.success("Note ajoutée.")
                    st.rerun()

            with col_act:
                st.subheader("⚠️ Complications & Statut")
                
                # Gestion Complications
                curr_comp = p['Complications']
                new_comp = st.selectbox("Déclarer Complication", ["RAS", "Infection Site Op", "Thrombose/Phlébite", "Escarre", "Lâchage Suture", "Choc"], index=0 if curr_comp=="RAS" else 0)
                if new_comp != "RAS" and new_comp != curr_comp:
                    st.session_state.patients.at[idx, 'Complications'] = new_comp
                    st.error(f"Complication {new_comp} enregistrée !")
                
                if curr_comp != "RAS":
                    st.error(f"ACTIVE : {curr_comp}")
                else:
                    st.success("Aucune complication active.")

                st.divider()
                # Mise à jour statut
                new_stat = st.selectbox("Nouveau Statut", ["Hospitalisé", "Bloc", "SSPI", "Sortie", "Consolidé", "Décès"], index=["Hospitalisé", "Bloc", "SSPI", "Sortie", "Consolidé", "Décès"].index(p['Statut']) if p['Statut'] in ["Hospitalisé", "Bloc", "SSPI", "Sortie", "Consolidé", "Décès"] else 0)
                if st.button("Mettre à jour Statut"):
                    st.session_state.patients.at[idx, 'Statut'] = new_stat
                    st.success("Statut modifié.")
                    st.rerun()

# ==============================================================================
# 3. FINANCE COMPLÈTE (Recettes & Dépenses)
# ==============================================================================
elif menu == "💰 FINANCE COMPLÈTE":
    st.title("Comptabilité du Service")
    
    t1, t2 = st.tabs(["📝 Saisie Mouvement", "📒 Grand Livre"])
    
    with t1:
        with st.form("fin_form"):
            c1, c2 = st.columns(2)
            with c1:
                m_type = st.radio("Type de Mouvement", ["Recette (Entrée)", "Dépense (Sortie)"], horizontal=True)
                date_op = st.date_input("Date", datetime.now())
                montant = st.number_input("Montant (GNF)", min_value=0, step=10000)
            with c2:
                if m_type == "Recette (Entrée)":
                    cat = st.selectbox("Catégorie", ["Paiement Patient", "Subvention", "Don", "Autre"])
                else:
                    cat = st.selectbox("Catégorie", ["Achat Matériel", "Pharmacie", "Salaires/Primes", "Maintenance", "Restauration", "Autre"])
                
                desc = st.text_input("Description (Ex: Nom Patient ou Facture Fournisseur)")
            
            if st.form_submit_button("Enregistrer Mouvement"):
                new_fin = {"Date": str(date_op), "Type": m_type.split(" ")[0], "Categorie": cat, "Description": desc, "Montant": montant}
                st.session_state.finances = pd.concat([st.session_state.finances, pd.DataFrame([new_fin])], ignore_index=True)
                st.success("Enregistré.")
    
    with t2:
        st.subheader("Historique des Opérations")
        # Colorer les montants
        def color_type(val):
            color = 'green' if val == 'Recette' else 'red'
            return f'color: {color}'
        
        if not df_fin.empty:
            st.dataframe(df_fin.style.map(color_type, subset=['Type']), use_container_width=True)
            
            # Bilan rapide
            tot_rec = df_fin[df_fin['Type'] == "Recette"]['Montant'].sum()
            tot_dep = df_fin[df_fin['Type'] == "Dépense"]['Montant'].sum()
            st.metric("SOLDE DE CAISSE", f"{tot_rec - tot_dep:,.0f} GNF", delta=f"R: {tot_rec} | D: {tot_dep}")
        else:
            st.info("Aucune transaction.")

# ==============================================================================
# 4. GESTION STOCKS (Entrées/Sorties)
# ==============================================================================
elif menu == "📦 GESTION STOCKS":
    st.title("Pharmacie & Matériel")
    
    col_list, col_act = st.columns([2, 1])
    
    with col_list:
        st.subheader("État du Stock")
        # Alerte visuelle stock bas
        st.dataframe(df_stk.style.highlight_between(left=0, right=df_stk['Seuil'], subset=['Qte'], color='#ffcccc'), use_container_width=True)
        
        # Liste des alertes
        alertes = df_stk[df_stk['Qte'] <= df_stk['Seuil']]
        if not alertes.empty:
            st.error("⚠️ COMMANDE NÉCESSAIRE :")
            st.table(alertes[['Item', 'Qte']])

    with col_act:
        st.subheader("Mise à Jour")
        
        # Sélection item
        item = st.selectbox("Article", df_stk['Item'])
        idx_s = df_stk[df_stk['Item'] == item].index[0]
        current_q = df_stk.at[idx_s, 'Qte']
        
        st.write(f"Stock actuel : **{current_q}**")
        
        action = st.radio("Action", ["Sortie (Utilisation)", "Entrée (Livraison)"])
        qty = st.number_input("Quantité", 1, 1000, 1)
        
        if st.button("Valider Mouvement"):
            if action == "Sortie (Utilisation)":
                if current_q >= qty:
                    st.session_state.stock.at[idx_s, 'Qte'] -= qty
                    st.success(f"Sortie de {qty} {item}.")
                else:
                    st.error("Stock insuffisant !")
            else:
                st.session_state.stock.at[idx_s, 'Qte'] += qty
                st.success(f"Entrée de {qty} {item}.")
            st.rerun()

        st.divider()
        with st.expander("Créer nouvel article"):
            new_item = st.text_input("Nom Article")
            new_init = st.number_input("Stock Initial", 0)
            new_seuil = st.number_input("Seuil Alerte", 0)
            if st.button("Créer Article"):
                new_row = {"Item": new_item, "Qte": new_init, "Seuil": new_seuil}
                st.session_state.stock = pd.concat([st.session_state.stock, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Article créé.")
                st.rerun()

# ==============================================================================
# 5. EXPORT
# ==============================================================================
elif menu == "💾 SAUVEGARDE":
    st.title("Export Données")
    st.write("Téléchargez vos registres.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        csv_p = df_pat.to_csv(index=False).encode('utf-8')
        st.download_button("📥 PATIENTS (CSV)", csv_p, "patients.csv")
    with c2:
        csv_f = df_fin.to_csv(index=False).encode('utf-8')
        st.download_button("📥 FINANCES (CSV)", csv_f, "finances.csv")
    with c3:
        csv_s = df_stk.to_csv(index=False).encode('utf-8')
        st.download_button("📥 STOCK (CSV)", csv_s, "stock.csv")
