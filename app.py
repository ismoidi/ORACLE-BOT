import streamlit as st
import time
from collections import Counter
from datetime import datetime, timedelta
import itertools
import asyncio
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================================
# 🔑 CONFIGURATION SÉCURISÉE DU SITE & DU BOT
# ==========================================
st.set_page_config(page_title="Oracle Cards Bot", page_icon="🔮", layout="centered")

UTILISATEURS_AUTORISES = {"admin": "oracle2026"}
for i in range(1, 11):
    UTILISATEURS_AUTORISES[f"ami{i}"] = f"ora{i}nx"

TOKEN_TELEGRAM = "8434603595:AAG5hkLGyXppK805olMcOTGxoOp3E2ATJ8O"
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
        if gagnant:
            (carte_nom, nb) = gagnant[0]
            return carte_nom, nb
    return None

# ==========================================
# 🤖 BOT TELEGRAM AUTOMATIQUE
# ==========================================
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔮 **Oracle Bot Actif !**\nEnvoyez un numéro de tour.")

async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = update.message.text.strip()
    if texte.isdigit():
        tour_actuel = int(texte)
        res = calculer_resultat_tour(tour_actuel)
        if res:
            carte_nom, nb = res
            await update.message.reply_text(f"🎯 Tour {tour_actuel} → 🃏 **{carte_nom}**")
        else:
            await update.message.reply_text(f"🎯 Aucun résultat.")

def lancer_bot_telegram():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = Application.builder().token(TOKEN_TELEGRAM).build()
        app.add_handler(CommandHandler("start", start_cmd))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
        app.run_polling(close_loop=False)
    except Exception:
        pass

if "bot_lance" not in st.session_state:
    st.session_state["bot_lance"] = True
    threading.Thread(target=lancer_bot_telegram, daemon=True).start()

# ==========================================
# 🌐 INTERFACE DU SITE STREAMLIT
# ==========================================
if "connecte" not in st.session_state: st.session_state["connecte"] = False
if "username" not in st.session_state: st.session_state["username"] = ""

if not st.session_state["connecte"]:
    st.title("🔒 Connexion - Oracle Bot")
    st.write("Veuillez entrer vos identifiants uniques.")
    
    identifiant = st.text_input("Identifiant (ex: ami1)")
    mot_de_passe = st.text_input("Mot de passe", type="password")
    
    if st.button("Valider la connexion"):
        if identifiant in UTILISATEURS_AUTORISES and UTILISATEURS_AUTORISES[identifiant] == mot_de_passe:
            st.session_state["connecte"] = True
            st.session_state["username"] = identifiant
            st.rerun()
        else: st.error("Identifiant ou mot de passe incorrect.")
    st.stop()

if st.session_state["username"] == "admin":
    with st.sidebar:
        st.title("👑 Dashboard Admin")
        for u, p in UTILISATEURS_AUTORISES.items():
            if u != "admin": st.write(f"🟢 **{u}** : `{p}`")

st.write(f"👤 Compte actif : **{st.session_state['username']}**")
if st.button("Déconnexion"):
    st.session_state["connecte"] = False
    st.rerun()

def obtenir_prochain_jeu_divisible_par_4():
    maintenant = obtenir_heure_niger()
    debut_jeux = maintenant.replace(hour=1, minute=0, second=0, microsecond=0)
    if maintenant < debut_jeux: debut_jeux -= timedelta(days=1)
    minute_actuelle = int((maintenant - debut_jeux).total_seconds() / 60) + 1
    prochain_tour = minute_actuelle + (4 - (minute_actuelle % 4)) if minute_actuelle % 4 != 0 else minute_actuelle + 4
    return prochain_tour, debut_jeux + timedelta(minutes=prochain_tour - 1)

st.markdown("---")
prochain_tour, heure_depart_jeu = obtenir_prochain_jeu_divisible_par_4()

st.info(f"🎮 **Analyse du tour en cours : {prochain_tour}**")

res_site = calculer_resultat_tour(prochain_tour)
if res_site:
    carte_nom, nb = res_site
    st.success(f"### 🃏 Carte recommandée : {carte_nom}")
else:
    st.warning("Aucune carte trouvée.")

temps_restant = int((heure_depart_jeu - obtenir_heure_niger()).total_seconds())
if temps_restant > 0:
    st.metric(label="⏳ Décompte avant le tour", value=f"{temps_restant // 60}m {temps_restant % 60}s")
    time.sleep(1)
    st.rerun()
else:
    st.success("静态 Nouveau tour !")
    time.sleep(2)
    st.rerun()
