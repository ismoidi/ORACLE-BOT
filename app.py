import streamlit as st
import time
from collections import Counter
from datetime import datetime, timedelta
import itertools

# Configuration visuelle du site
st.set_page_config(page_title="Oracle Cards Bot", page_icon="🔮", layout="centered")

TABLE_EXTRACTION = {
    1: 8, 2: 6, 3: 1, 4: 3, 5: 7, 6: 6, 7: 2, 8: 4, 9: 0, 10: 7,
    11: 9, 12: 5, 13: 1, 14: 5, 15: 1, 16: 1, 17: 3, 18: 2, 19: 6, 20: 5,
    21: 0, 22: 6, 23: 6, 24: 3, 25: 3, 26: 2, 27: 3, 28: 1, 29: 2, 30: 4,
    31: 3, 32: 4, 33: 1, 34: 0, 35: 3, 36: 2, 37: 2, 38: 3, 39: 6, 40: 1,
    41: 4, 42: 5, 43: 3, 44: 1, 45: 0, 46: 4, 47: 8, 48: 0, 49: 5, 50: 1,
    51: 5, 52: 0, 53: 1, 54: 0, 55: 2, 56: 4, 57: 0, 58: 0, 59: 0, 60: 0,
    61: 0, 62: 0, 63: 0, 64: 0, 65: 0, 66: 0
}

SUITE_CHIFFRES = "861376246795151132650663323212434102323614551048051501624000000000"

def determiner_carte_par_ordre_avec_jour(index_jeu, date_actuelle):
    if not SUITE_CHIFFRES or index_jeu <= 0:
        return None
    enseignes = ["Pique ♠️", "Trèfle ♣️", "Carreau ♦️", "Cœur ❤️"]
    decalage_jour = date_actuelle.day
    index_chiffre = (index_jeu - 1 + decalage_jour) % len(SUITE_CHIFFRES)
    chiffre_extrait = SUITE_CHIFFRES[index_chiffre]
    
    # Correction demandée : On garde uniquement l'enseigne visuelle (symbole)
    enseigne_actuelle = enseignes[index_chiffre % 4].split()[-1] 
    return enseigne_actuelle

def obtenir_prochain_jeu_divisible_par_4():
    maintenant = datetime.now()
    debut_jeux = maintenant.replace(hour=1, minute=0, second=0, microsecond=0)
    if maintenant < debut_jeux:
        debut_jeux -= timedelta(days=1)
    minute_actuelle = int((maintenant - debut_jeux).total_seconds()) // 60 + 1
    if minute_actuelle % 4 == 0:
        prochain_tour = minute_actuelle + 4
    else:
        prochain_tour = minute_actuelle + (4 - (minute_actuelle % 4))
    heure_depart_jeu = debut_jeux + timedelta(minutes=prochain_tour - 4)
    if prochain_tour > 1440:
        prochain_tour = 4
        return prochain_tour, heure_depart_jeu
    return prochain_tour, heure_depart_jeu

# --- SYSTÈME DE CONNEXION ---
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
else:
    # --- AFFICHAGE MODIFIÉ SELON VOS EXIGENCES ---
    st.title("🃏 Cartes du joueur + 2 rattrapage")
    
    # Calcul automatique exact du tour et du temps
    tour_actuel, heure_jeu = obtenir_prochain_jeu_divisible_par_4()
    symbole_carte = determiner_carte_par_ordre_avec_jour(tour_actuel, datetime.now())
    
    # Rendu final demandé : "Numéro du tour + Symbole de la carte" (Ex: 495 ♣️)
    st.success(f"{tour_actuel} {symbole_carte}")
    
    st.caption(f"Connecté en tant que : {st.session_state['utilisateur']}")
    if st.button("Se déconnecter"):
        st.session_state["authentifie"] = False
        st.rerun()
