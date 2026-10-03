import streamlit as st
import time
from collections import Counter
from datetime import datetime, timedelta
import itertools

# Configuration visuelle du site
st.set_page_config(page_title="Oracle Cards Bot - Sécurisé", page_icon="🔮", layout="centered")

# ==========================================
# 🔑 ZONE DE CONTRÔLE DES UTILISATEURS (Gestion des accès)
# ==========================================
# Vous pouvez modifier les identifiants et les mots de passe ici à tout moment.
UTILISATEURS_AUTORISES = {
    "admin": "oracle2026",    # Votre compte personnel
    "ami1": "niger77",       # Compte pour votre premier ami
    "ami2": "cards88"        # Compte pour votre deuxième ami
}

# Initialisation de la session
if "connecte" not in st.session_state:
    st.session_state["connecte"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# Interface de connexion verrouillée
if not st.session_state["connecte"]:
    st.title("🔒 Accès Sécurisé - Oracle Bot")
    st.markdown("Veuillez entrer vos identifiants personnels pour accéder au bot.")
    
    identifiant = st.text_input("Identifiant utilisateur")
    mot_de_passe = st.text_input("Mot de passe", type="password")
    
    if st.button("Se connecter"):
        if identifiant in UTILISATEURS_AUTORISES and UTILISATEURS_AUTORISES[identifiant] == mot_de_passe:
            st.session_state["connecte"] = True
            st.session_state["username"] = identifiant
            st.success("Connexion réussie !")
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect. Accès refusé.")
    st.stop()

# ==========================================
# 🎮 LOGIQUE DE L'APPLICATION (Une fois connecté)
# ==========================================

col_user, col_logout = st.columns([2, 1])
with col_user:
    st.write(f"👤 Connecté en tant que : **{st.session_state['username']}**")
with col_logout:
    if st.button("Déconnexion"):
        st.session_state["connecte"] = False
        st.session_state["username"] = ""
        st.rerun()

TABLE_EXTRACTION = {
    1: 8, 2: 6, 3: 1, 4: 3, 5: 7, 6: 6, 7: 2, 8: 4, 9: 6, 10: 7,
    11: 9, 12: 5, 13: 1, 14: 5, 15: 1, 16: 1, 17: 3, 18: 2, 19: 6, 20: 5,
    21: 0, 22: 6, 23: 6, 24: 3, 25: 3, 26: 2, 27: 3, 28: 1, 29: 2, 30: 4,
    31: 3, 32: 4, 33: 1, 34: 0, 35: 3, 36: 2, 37: 2, 38: 3, 39: 6, 40: 1,
    41: 4, 42: 5, 43: 5, 44: 1, 45: 0, 46: 4, 47: 8, 48: 0, 49: 5, 50: 1,
    51: 5, 52: 0, 53: 1, 54: 6, 55: 2, 56: 4, 57: 0, 58: 0, 59: 0, 60: 0,
    61: 0, 62: 0, 63: 0, 64: 0, 65: 0, 66: 0
}

SUITE_CHIFFRES = "861376246795151132650663323124341032236145510480515016240000000000"

def determiner_carte_par_ordre_avec_jour(index_jeu, date_actuelle):
    if not SUITE_CHIFFRES or index_jeu <= 0:
        return None
    enseignes = ["Pique ♠️", "Trèfle ♣️", "Carreau ♦️", "Cœur ♥️"]
    decalage_jour = date_actuelle.day
    index_chiffre = (index_jeu - 1 + decalage_jour) % len(SUITE_CHIFFRES)
    chiffre_extrait = SUITE_CHIFFRES[index_chiffre]
    enseigne_actuelle = enseignes[index_chiffre % 4]
    valeur_carte = "10" if chiffre_extrait == '0' else chiffre_extrait
    return f"{valeur_carte} de {enseigne_actuelle}"

def obtenir_prochain_jeu_divisible_par_4():
    maintenant = datetime.now()
    debut_jeux = maintenant.replace(hour=1, minute=0, second=0, microsecond=0)
    if maintenant < debut_jeux:
        debut_jeux -= timedelta(days=1)
    minute_actuelle = int((maintenant - debut_jeux).total_seconds() / 60) + 1
    if minute_actuelle % 4 == 0:
        prochain_tour = minute_actuelle + 4
    else:
        prochain_tour = minute_actuelle + (4 - (minute_actuelle % 4))
    heure_depart_jeu = debut_jeux + timedelta(minutes=prochain_tour - 1)
    if prochain_tour > 1440:
        prochain_tour = 4
    return prochain_tour, heure_depart_jeu

st.title("🔮 Oracle Cards - Anticipateur Automatique")
st.markdown("---")

maintenant = datetime.now()
prochain_tour, heure_depart_jeu = obtenir_prochain_jeu_divisible_par_4()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="📅 Jour du mois actif", value=f"Jour {maintenant.day}")
with col2:
    st.metric(label="⏰ Prochain Tour à", value=heure_depart_jeu.strftime("%H:%M:%S"))

st.info(f"🎮 **Tour calculé en préparation : {prochain_tour}**")

chiffres_tour = [int(c) for c in str(prochain_tour) if c != '0']
if len(chiffres_tour) < 2:
    paires = [(chiffres_tour, chiffres_tour)]
else:
    paires = list(itertools.combinations(chiffres_tour, 2))

positions_traitees = set()
for c1, c2 in paires:
    debut = min(c1, c2)
    fin = max(c1, c2)
    intervalle = list(range(debut, fin + 1))
    for pos in intervalle:
        positions_traitees.add(pos)

cartes_trouvees = []
for position_grille in sorted(positions_traitees):
    if position_grille in TABLE_EXTRACTION:
        index_cible = TABLE_EXTRACTION[position_grille]
        carte = determiner_carte_par_ordre_avec_jour(index_cible, maintenant)
        if carte:
            cartes_trouvees.append(carte)

st.subheader("🎯 CARTE RECOMMANDÉE POUR CE TOUR")
if cartes_trouvees:
    compteur = Counter(cartes_trouvees)
    gagnant = compteur.most_common(1)[0]
    carte_la_plus_repetee, nb_repetitions = gagnant
    st.success(f"### 🃏 {carte_la_plus_repetee} (Trouvée {nb_repetitions}x)")
else:
    st.warning("Aucune carte trouvée pour cette combinaison.")

st.markdown("---")
temps_restant_container = st.empty()
temps_restant = int((heure_depart_jeu - datetime.now()).total_seconds())

if temps_restant > 0:
    mins, secs = divmod(temps_restant, 60)
    temps_restant_container.metric(label="⏳ Décompte avant le tour", value=f"{mins}m {secs}s")
    time.sleep(1)
    st.rerun()
else:
    st.success("🔔 Le tour commence ! Calcul du tour suivant...")
    time.sleep(2)
    st.rerun()
