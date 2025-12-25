import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# ==============================================================================
# 1. CONFIGURATION & DESIGN (MODE HD)
# ==============================================================================
st.set_page_config(page_title="SAMProb Expert", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

# --- DESIGN SYSTÈME MÉDICAL ---
st.markdown("""
    <style>
    /* TYPOGRAPHIE ET LISIBILITÉ */
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; font-size: 18px !important; color: #1e1e1e !important; }
    .stApp { background-color: #f8f9fa; }
    
    /* EN-TÊTES */
    h1 { color: #2e7d32 !important; font-size: 2.5rem !important; border-bottom: 2px solid #2e7d32; text-transform: uppercase; }
    h2, h3 { color: #1b5e20 !important; }
    
    /* ZONES DE RÉPONSE IA */
    .ai-box {
        background-color: #ffffff; 
        border-left: 5px solid #2e7d32; 
        padding: 20px; 
        border-radius: 8px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* BOUTONS TACTILES */
    .stButton>button { 
        height: 3.5em !important; 
        font-size: 20px !important; 
        border-radius: 8px !important; 
        font-weight: bold;
        border: none;
        width: 100%;
    }
    /* Bouton principal vert médical */
    .stButton>button { background-color: #2e7d32; color: white; }
    
    /* ALERTE URGENCE */
    .urgence-box { background-color: #ffebee; border: 2px solid #c62828; color: #c62828; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SÉCURITÉ (LOGIN)
# ==============================================================================
if 'auth_sam' not in st.session_state: st.session_state.auth_sam = False

def check_login():
    # MOT DE PASSE : SAMPROB2025
    if st.session_state.pwd_sam == "SAMPROB2025":
        st.session_state.auth_sam = True
        del st.session_state.pwd_sam
    else: st.error("Accès Refusé")

if not st.session_state.auth_sam:
    st.markdown("<br><br><h1 style='text-align:center'>🧬 SAMProb</h1><h3 style='text-align:center'>SYSTEME D'AIDE MEDICALE</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.text_input("CODE D'ACTIVATION", type="password", key="pwd_sam", on_change=check_login)
        st.button("INITIALISER LE SYSTÈME", on_click=check_login)
    st.stop()

# ==============================================================================
# 3. MOTEUR INTELLIGENCE (GEMINI)
# ==============================================================================
class Brain:
    def __init__(self):
        self.model = None
        self.api_valid = False

    def connect(self, key):
        try:
            genai.configure(api_key=key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.api_valid = True
            return True
        except: return False

    def analyze(self, prompt, image=None):
        if not self.api_valid: return "⚠️ ERREUR : Clé API non connectée (Voir Menu)."
        
        # PROMPT SYSTÈME : RÔLE DE CHEF DE CLINIQUE
        sys_prompt = """Tu es SAMProb, un assistant expert en Chirurgie et Médecine d'Urgence au CHU Donka.
        Tes réponses doivent être structurées comme un avis médical senior :
        1. 🔬 HYPOTHÈSES DIAGNOSTIQUES (Probabilités)
        2. 📝 BILAN À DEMANDER (Examens complémentaires)
        3. 💊 CONDUITE À TENIR (Traitement immédiat)
        Sois concis, direct et professionnel."""
        
        try:
            content = [sys_prompt, prompt]
            if image: content.append(image)
            response = self.model.generate_content(content)
            return response.text
        except Exception as e: return f"Erreur réseau : {e}"

if 'brain' not in st.session_state: st.session_state.brain = Brain()

# ==============================================================================
# 4. INTERFACE PRINCIPALE
# ==============================================================================
with st.sidebar:
    st.title("🧬 SAMProb V2")
    st.caption("Dr. SAMAKÉ")
    st.write("---")
    menu = st.radio("MODULES", ["💬 AVIS MÉDICAL (IA)", "👁️ ANALYSE VISUELLE", "🧮 CALCULATEURS", "⚡ PROTOCOLES URGENCE", "⚙️ CONFIGURATION"])
    st.write("---")
    if st.button("🔒 VERROUILLER"):
        st.session_state.auth_sam = False
        st.rerun()

# --- MODULE 1 : AVIS MÉDICAL ---
if menu == "💬 AVIS MÉDICAL (IA)":
    st.title("CONSULTATION IA")
    st.info("Décrivez le cas clinique. SAMProb structure la réponse.")
    
    # Historique de chat simplifié pour la clarté
    if 'history' not in st.session_state: st.session_state.history = []
    
    for msg in st.session_state.history:
        if msg['role'] == 'user':
            st.markdown(f"<div style='background:#e3f2fd;padding:15px;border-radius:10px;text-align:right'><b>Dr. Samaké :</b><br>{msg['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-box'><b>🧬 SAMProb :</b><br>{msg['text']}</div>", unsafe_allow_html=True)
            
    user_input = st.chat_input("Ex: Patient 30 ans, AVP Moto, Douleur hanche droite, TA 9/6...")
    if user_input:
        st.session_state.history.append({"role": "user", "text": user_input})
        with st.spinner("Analyse du cas en cours..."):
            resp = st.session_state.brain.analyze(user_input)
            st.session_state.history.append({"role": "ai", "text": resp})
        st.rerun()

# --- MODULE 2 : VISION (X-RAY / PLAIE) ---
elif menu == "👁️ ANALYSE VISUELLE":
    st.title("VISION PAR ORDINATEUR")
    st.write("Analysez Radios, ECG, ou Plaies.")
    
    mode = st.radio("Source", ["📸 Caméra", "📁 Importer"], horizontal=True)
    img_file = st.camera_input("Scanner") if mode == "📸 Caméra" else st.file_uploader("Fichier")
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="Image capturée", width=300)
        
        type_analyse = st.selectbox("Type d'analyse", ["Traumatologie (Radio/Scanner)", "Dermatologie (Plaie/Infection)", "Cardiologie (ECG)"])
        
        if st.button("LANCER L'ANALYSE EXPERTE"):
            with st.spinner("Lecture de l'image..."):
                prompt = f"Analyse cette image médicale en tant qu'expert en {type_analyse}. Décris les anomalies visibles et propose une conclusion."
                res = st.session_state.brain.analyze(prompt, img)
                st.markdown(f"<div class='ai-box'>{res}</div>", unsafe_allow_html=True)

# --- MODULE 3 : CALCULATEURS (NOUVEAU) ---
elif menu == "🧮 CALCULATEURS":
    st.title("SCORES CLINIQUES")
    
    tab1, tab2 = st.tabs(["GLASGOW (GCS)", "WELLS (TVP)"])
    
    with tab1:
        st.subheader("Score de Glasgow")
        yeux = st.selectbox("Ouverture des Yeux", ["Spontanée (4)", "À la voix (3)", "À la douleur (2)", "Nulle (1)"])
        verbal = st.selectbox("Réponse Verbale", ["Orientée (5)", "Confuse (4)", "Inappropriée (3)", "Incompréhensible (2)", "Nulle (1)"])
        moteur = st.selectbox("Réponse Motrice", ["Ordre (6)", "Orientée (5)", "Evitement (4)", "Flexion (3)", "Extension (2)", "Nulle (1)"])
        
        score = int(yeux[-2]) + int(verbal[-2]) + int(moteur[-2])
        
        st.metric("SCORE GCS", f"{score} / 15")
        if score <= 8: st.error("⚠️ COMA GRAVE -> INTUBATION ?")
        elif score <= 12: st.warning("⚠️ TRAUMA MODÉRÉ")
        else: st.success("✅ CONSCIENCE NORMALE/LÉGÈRE")

    with tab2:
        st.subheader("Score de Wells (Suspicion TVP)")
        s1 = st.checkbox("Cancer actif (+1)")
        s2 = st.checkbox("Paralysie / Immobilisation plâtrée (+1)")
        s3 = st.checkbox("Alitement > 3j ou Chirurgie majeure < 4 sem (+1)")
        s4 = st.checkbox("Douleur sur trajet veineux (+1)")
        s5 = st.checkbox("Oedème tout le membre (+1)")
        s6 = st.checkbox("Oedème mollet > 3cm par rapport à l'autre (+1)")
        
        total_wells = sum([s1, s2, s3, s4, s5, s6])
        st.metric("SCORE WELLS", total_wells)
        if total_wells >= 2: st.error("PROBABILITÉ FORTE -> ÉCHO DOPPLER")
        else: st.success("PROBABILITÉ FAIBLE -> D-DIMÈRES")

# --- MODULE 4 : PROTOCOLES (OFFLINE) ---
elif menu == "⚡ PROTOCOLES URGENCE":
    st.title("PROTOCOLES VITAUX")
    st.caption("Accessibles hors-connexion")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("❤️ ARRÊT CARDIAQUE (ACLS)"):
            st.markdown("""
            <div class='urgence-box'>
            <h3>ALGORITHME ACR</h3>
            1. <b>MCE</b> : 100-120/min (30:2)<br>
            2. <b>CHOC</b> : Si FV/TV sans pouls (Biphasique 200J)<br>
            3. <b>ADRÉNALINE</b> : 1mg IV toutes les 3-5 min<br>
            4. <b>AMIODARONE</b> : 300mg IV après 3e choc
            </div>
            """, unsafe_allow_html=True)
            
    with c2:
        if st.button("💉 CHOC ANAPHYLACTIQUE"):
            st.markdown("""
            <div class='urgence-box'>
            <h3>CHOC ANAPHYLAXIE</h3>
            1. <b>ADRÉNALINE IM</b> (Cuisse)<br>
               -> 0.5 mg (Adulte) | 0.01 mg/kg (Enfant)<br>
            2. <b>REMPLISSAGE</b> : Cristalloïdes 20ml/kg<br>
            3. <b>CORTICOÏDES</b> : Solumedrol 1-2 mg/kg
            </div>
            """, unsafe_allow_html=True)

# --- MODULE 5 : CONFIG ---
elif menu == "⚙️ CONFIGURATION":
    st.title("RÉGLAGES")
    api_key = st.text_input("CLÉ API GOOGLE (Gemini)", type="password")
    if api_key:
        if st.session_state.brain.connect(api_key):
            st.success("✅ CERVEAU IA CONNECTÉ ET PRÊT")
        else:
            st.error("❌ Clé invalide")

