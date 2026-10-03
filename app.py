import streamlit as st
import time
from collections import Counter
from datetime import datetime, timedelta
import itertools

# Configuration visuelle du site
st.set_page_config(page_title="Oracle Cards Bot - Admin Control", page_icon="🔮", layout="centered")

# ==========================================
# 🔑 GENERATION SECURISEE DES ACCÈS UTILISATEURS
# ==========================================
UTILISATEURS_AUTORISES = {
    "admin": "oracle2026"  # Votre compte Maître personnel
}

# Génération des mots de passe (Format: oraXnx)
for i in range(1, 11):
    UTILISATEURS_AUTORISES[f"ami{i}"] = f"ora{i}nx"

# Fonction pour obtenir l'heure exacte du Niger (UTC+1)
def obtenir_heure_niger():
    return datetime.utcnow() + timedelta(hours=1)

# Système de stockage des connexions en mémoire vive
if "historique_connexions" not in st.session_state:
    st.session_state["historique_connexions"] = [
        {"heure": obtenir_heure_niger().strftime("%H:%M:%S"), "user": "System", "action": "Démarrage du serveur"}
    ]

# Initialisation de la session de connexion
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
            
            # Enregistrement dans l'historique
            nouvelle_connexion = {
                "heure": obtenir_heure_niger().strftime("%H:%M:%S"),
                "user": identifiant,
                "action": "Connexion réussie"
            }
            st.session_state["historique_connexions"].append(nouvelle_connexion)
            st.success("Connexion réussie !")
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect. Accès refusé.")
    st.stop()

# ==========================================
# 📊 PANNEAU DE SURVEILLANCE EXCLUSIF ADMIN
# ==========================================
if st.session_state["username"] == "admin":
    with st.sidebar:
        st.title("👑 Dashboard Admin")
        st.write("Contrôle des 10 accès utilisateurs en direct.")
        
        st.subheader("👥 Statut des comptes")
        for u in UTILISATEURS_AUTORISES.keys():
            if u != "admin":
                st.write(f"🟢 **{u}** : Actif (`{UTILISATEURS_AUTORISES[u]}`)")
                
        st.markdown("---")
        st.subheader("📋 Historique de cette session")
        for log in reversed(st.session_state["historique_connexions"]):
            st.caption(f"[{log['heure']}] **{log['user']}** : {log['action']}")

# Bouton de déconnexion
col_user, col_logout = st.columns(2)
with col_user:
    st.write(f"👤 Connecté en tant que : **{st.session_state['username']}**")
with col_logout:
    if st.button("Déconnexion"):
        st.session_state["connecte"] = False
        st.session_state["username"] = ""
        st.rerun()

# ==========================================
# 🎮 LOGIQUE DE L'APPLICATION
# ==========================================
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
    enseignes = ["Pique", "Trèfle", "Carreau", "Cœur"]
    decalage_jour = date_actuelle.day
    index_chiffre = (index_jeu - 1 + decalage_jour) % len(SUITE_CHIFFRES)
    chiffre_extrait = SUITE_CHIFFRES[index_chiffre]
    enseigne_actuelle = enseignes[index_chiffre % 4]
    valeur_carte = "10" if chiffre_extrait == '0' else chiffre_extrait
    # Format simplifié demandé : "Valeur Enseigne"
    return f"{valeur_carte} {enseigne_actuelle}"

def obtenir_prochain_jeu_divisible_par_4():
    maintenant = obtenir_heure_niger()
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

# Affichage de l'horloge synchronisée du Niger
maintenant_niger = obtenir_heure_niger()
st.write(f"## ⏰ Horloge Niger : {maintenant_niger.strftime('%H:%M:%S')}")
st.markdown("---")

prochain_tour, heure_depart_jeu = obtenir_prochain_jeu_divisible_par_4()

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
        carte = determiner_carte_par_ordre_avec_jour(index_cible, maintenant_niger)
        if carte:
            cartes_trouvees.append(carte)

st.subheader("🎯 CARTE RECOMMANDÉE POUR CE TOUR")
if cartes_trouvees:
    compteur = Counter(cartes_trouvees)
    gagnant = compteur.most_common(1)
    
    if gagnant:
        carte_la_plus_repetee = gagnant[0][0]
        nb_repetitions = gagnant[0][1]
        st.success(f"### 🃏 {carte_la_plus_repetee} (Trouvée {nb_repetitions}x)")
    else:
        st.warning("Aucune carte trouvée.")
else:
    st.warning("Aucune carte trouvée pour cette combinaison.")

st.markdown("---")
temps_restant_container = st.empty()
temps_restant = int((heure_depart_jeu - obtenir_heure_niger()).total_seconds())

if temps_restant > 0:
    mins, secs = divmod(temps_restant, 60)
    temps_restant_container.metric(label="⏳ Décompte avant le tour", value=f"{mins}m {secs}s")
    time.sleep(1)
    st.rerun()
else:
    st.success("🔔 Le tour commence ! Calcul du tour suivant...")
    time.sleep(2)
    st.rerun()
