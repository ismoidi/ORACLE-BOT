import streamlit as st

# Configuration de la page pour mobile
st.set_page_config(page_title="Oracle Cards Bot", layout="centered")

# --- 1. SYSTÈME DE SÉCURITÉ ET DE CONNEXION ---
# (Votre liste d'utilisateurs autorisés)
COMPTES_AUTORISES = {
    "admin": "oracle2026",
    "joueur1": "cartes2026"
}

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

if not st.session_state["authentifie"]:
    st.title("🔒 Connexion - Oracle Bot")
    
    identifiant = st.text_input("Identifiant unique")
    mot_de_passe = st.text_input("Mot de passe", type="password")
    
    if st.button("Valider la connexion", use_container_width=True):
        if identifiant in COMPTES_AUTORISES and mot_de_passe == COMPTES_AUTORISES[identifiant]:
            st.session_state["authentifie"] = True
            st.session_state["utilisateur"] = identifiant
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect.")

# --- 2. LOGIQUE DE CALCUL AUTOMATIQUE DU BOT ---
else:
    # Titre épuré demandé
    st.title("🃏 Cartes du joueur + 2 rattrapage")
    
    # Récupération automatique du tour en cours (remplacer par votre formule de calcul si nécessaire)
    if "numero_tour" not in st.session_state:
        st.session_state["numero_tour"] = 495  # Reprend là où le bot s'était arrêté
        
    # Dictionnaire des symboles visuels
    symboles = {
        "Trèfle": "♣️",
        "Pique": "♠️",
        "Cœur": "❤️",
        "Carreau": "♦️"
    }
    
    # Logique automatique : Le bot choisit la couleur selon le tour (Exemple de formule automatique)
    # Vous pouvez ajuster cette formule mathématique selon vos besoins réels
    if st.session_state["numero_tour"] % 4 == 0:
        couleur_calculee = "Trèfle"
    elif st.session_state["numero_tour"] % 4 == 1:
        couleur_calculee = "Pique"
    elif st.session_state["numero_tour"] % 4 == 2:
        couleur_calculee = "Cœur"
    else:
        couleur_calculee = "Carreau"
        
    symbole_actif = symboles[couleur_calculee]

    # Bouton automatique géré par le bot pour actualiser le calcul du tour
    if st.button("🔄 Lancer le calcul automatique du tour", use_container_width=True):
        st.session_state["numero_tour"] += 1
        st.rerun()

    # --- 3. AFFICHAGE ÉPURÉ CORRIGÉ ---
    # Affiche uniquement le numéro du tour calculé et le symbole associé (Ex: 495 ♣️)
    st.success(f"{st.session_state['numero_tour']} {symbole_actif}")
    
    # Option de déconnexion pour la sécurité
    st.caption(f"Connecté en tant que : {st.session_state['utilisateur']}")
    if st.button("Se déconnecter"):
        st.session_state["authentifie"] = False
        st.rerun()
        
