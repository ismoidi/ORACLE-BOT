import streamlit as st
from collections import Counter
from datetime import datetime, timedelta
import itertools

# Configuration de base épurée pour la Mini-App Telegram
st.set_page_config(page_title="Oracle", page_icon="🔮", layout="centered")

SUITE_CHIFFRES = "861376246795151132650663323124341032236145510480515016240000000000"

TABLE_EXTRACTION = {
    1: 8, 2: 6, 3: 1, 4: 3, 5: 7, 6: 6, 7: 2, 8: 4, 9: 6, 10: 7,
    11: 9, 12: 5, 13: 1, 14: 5, 15: 1, 16: 1, 17: 3, 18: 2, 19: 6, 20: 5,
    21: 0, 22: 6, 23: 6, 24: 3, 25: 3, 26: 2, 27: 3, 28: 1, 29: 2, 30: 4,
    31: 3, 32: 4, 33: 1, 34: 0, 35: 3, 36: 2, 37: 2, 38: 3, 39: 6, 40: 1,
    41: 4, 42: 5, 43: 5, 44: 1, 45: 0, 46: 4, 47: 8, 48: 0, 49: 5, 50: 1,
    51: 5, 52: 0, 53: 1, 54: 6, 55: 2, 56: 4, 57: 0, 58: 0, 59: 0, 60: 0,
    61: 0, 62: 0, 63: 0, 64: 0, 65: 0, 66: 0
}

def obtenir_heure_niger():
    return datetime.utcnow() + timedelta(hours=1)

def determiner_carte_par_ordre_absolu(index_jeu):
    if not SUITE_CHIFFRES or index_jeu <= 0: return None
    enseignes = ["Pique ♠️", "Trèfle ♣️", "Carreau ♦️", "Cœur ♥️"]
    index_chiffre = (index_jeu - 1) % len(SUITE_CHIFFRES)
    chiffre_extrait = SUITE_CHIFFRES[index_chiffre]
    enseigne_actuelle = enseignes[index_chiffre % 4]
    valeur_carte = "10" if chiffre_extrait == '0' else chiffre_extrait
    return f"{valeur_carte} de {enseigne_actuelle}"

def calculer_resultat_tour(prochain_tour):
    chiffres_tour = [int(c) for c in str(prochain_tour) if c != '0']
    if not chiffres_tour: return None
    if len(chiffres_tour) < 2: paires = [(chiffres_tour, chiffres_tour)]
    else: paires = list(itertools.combinations(chiffres_tour, 2))
    
    positions_traitees = set()
    for c1, c2 in paires:
        debut, fin = min(c1, c2), max(c1, c2)
        for pos in range(debut, fin + 1): positions_traitees.add(pos)
        
    cartes_trouvees = []
    for pos in sorted(positions_traitees):
        if pos in TABLE_EXTRACTION:
            carte = determiner_carte_par_ordre_absolu(TABLE_EXTRACTION[pos])
            if carte: cartes_trouvees.append(carte)
            
    if cartes_trouvees:
        compteur = Counter(cartes_trouvees)
        gagnant = compteur.most_common(1)
        if gagnant and len(gagnant) > 0:
            res_carte, nb = gagnant[0]
            return res_carte
    return None

def obtenir_prochain_jeu_divisible_par_4():
    maintenant = obtenir_heure_niger()
    debut_jeux = maintenant.replace(hour=1, minute=0, second=0, microsecond=0)
    if maintenant < debut_jeux: debut_jeux -= timedelta(days=1)
    minute_actuelle = int((maintenant - debut_jeux).total_seconds() / 60) + 1
    prochain_tour = minute_actuelle + (4 - (minute_actuelle % 4)) if minute_actuelle % 4 != 0 else minute_actuelle + 4
    return prochain_tour

# 1️⃣ Calcul du numéro de tour réel
tour_reel = obtenir_prochain_jeu_divisible_par_4()

# 2️⃣ Application de la loi de moins 1
tour_loi_appliquee = tour_reel - 1

# 3️⃣ Affichage clair à l'écran
st.info(f"🎮 **Numéro du jeu : {tour_loi_appliquee}**")

carte_recommandee = calculer_resultat_tour(tour_loi_appliquee)
if carte_recommandee:
    st.success(f"### 🃏 {carte_recommandee}")
else:
    st.write("🔄 Analyse en cours...")
