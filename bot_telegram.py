import asyncio
import itertools
import threading
import os
import logging
from collections import Counter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask
from telegram.ext import ApplicationBuilder

# Configuration des logs
logging.basicConfig(level=logging.INFO)

# 🔑 Configuration
TOKEN_TELEGRAM = "8434603595:AAG5hkLGyXppK805olMcOTGxo0p3E2ATJ80"
CHAT_ID = "-1003983624932"

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

# --- Serveur HTTP Flask ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Oracle Bot is Online and Running!", 200

# --- Logique de calcul ---
def obtenir_heure_niger():
    return datetime.now(ZoneInfo("Africa/Niamey"))

def determiner_carte_par_ordre_absolu(index_jeu):
    if not SUITE_CHIFFRES or index_jeu <= 0:
        return None
    enseignes = ["Pique ♠️", "Trèfle ♣️", "Carreau ♦️", "Cœur ♥️"]
    index_chiffre = (index_jeu - 1) % len(SUITE_CHIFFRES)
    chiffre_extrait = SUITE_CHIFFRES[index_chiffre]
    enseigne_actuelle = enseignes[index_chiffre % 4]
    valeur_carte = "10" if chiffre_extrait == '0' else chiffre_extrait
    return f"{valeur_carte} de {enseigne_actuelle}"

def calculer_resultat_tour(prochain_tour):
    chiffres_tour = [int(c) for c in str(prochain_tour) if c != '0']
    if not chiffres_tour:
        return None
    paires = [(chiffres_tour[0], chiffres_tour[0])] if len(chiffres_tour) < 2 else list(itertools.combinations(chiffres_tour, 2))
    positions_traitees = set()
    for c1, c2 in paires:
        for pos in range(min(c1, c2), max(c1, c2) + 1):
            positions_traitees.add(pos)
    cartes_trouvees = [determiner_carte_par_ordre_absolu(TABLE_EXTRACTION[pos]) for pos in sorted(positions_traitees) if pos in TABLE_EXTRACTION and determiner_carte_par_ordre_absolu(TABLE_EXTRACTION[pos])]
    if cartes_trouvees:
        gagnant = Counter(cartes_trouvees).most_common(1)
        if gagnant:
            return gagnant[0][0]
    return None

def obtenir_prochain_jeu_divisible_par_4():
    maintenant = obtenir_heure_niger()
    debut_jeux = maintenant.replace(hour=1, minute=0, second=0, microsecond=0)
    if maintenant < debut_jeux:
        debut_jeux = debut_jeux - timedelta(days=1)
    minute_actuelle = int((maintenant - debut_jeux).total_seconds() / 60) + 1
    return minute_actuelle + (4 - (minute_actuelle % 4)) if minute_actuelle % 4 != 0 else minute_actuelle + 4

async def boucle_envoi_telegram():
    app_bot = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    await app_bot.initialize()
    await app_bot.start()
    
    dernier_tour_envoye = None
    derniere_minute_envoyee = None
    logging.info("Boucle d'envoi Telegram démarrée.")

    while True:
        try:
            maintenant = obtenir_heure_niger()
            minute_cle = maintenant.strftime("%Y-%m-%d %H:%M")
            
            tour_reel = obtenir_prochain_jeu_divisible_par_4()
            tour_loi_appliquee = tour_reel - 1

            if tour_loi_appliquee != dernier_tour_envoye and minute_cle != derniere_minute_envoyee:
                carte = calculer_resultat_tour(tour_loi_appliquee) or "Analyse en cours..."
                heure_actuelle = maintenant.strftime("%H:%M:%S")

                message = (
                    f"🔮 **ORACLE PREDICTION**\n"
                    f"🕒 Heure : `{heure_actuelle}`\n\n"
                    f"🎮 **Numéro du jeu : {tour_loi_appliquee}**\n"
                    f"🃏 **Carte recommandée : {carte}**"
                )

                await app_bot.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
                logging.info(f"Message envoyé pour le jeu {tour_loi_appliquee}")
                
                dernier_tour_envoye = tour_loi_appliquee
                derniere_minute_envoyee = minute_cle

        except Exception as e:
            logging.error(f"Erreur durant l'envoi : {e}")

        await asyncio.sleep(15)

def lancer_bot_background():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(boucle_envoi_telegram())

if __name__ == '__main__':
    t = threading.Thread(target=lancer_bot_background, daemon=True)
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
