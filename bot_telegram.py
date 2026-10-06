import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from flask import Flask
import telebot
import asyncio
from telethon import TelegramClient, events

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
TELEGRAM_TOKEN = "8434603595:AAEtNoqtct5sH-0erJFxkhUQAqrVRuzPXvk"
CHAT_ID_CIBLE = "-1003983624932"

# Identifiants API (my.telegram.org)
API_ID = 36011582
API_HASH = "1a59e486bbe7867994bae4450a958f7c"
CANAL_SOURCE = "jokerwcbnn11280"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Séquence 52!
SEQUENCE_52 = "861376246795151132650663323124341032236145510480515016240000000000"

# Ordre des enseignes (Pique ♠️, Trèfle ♣️, Carreau ♦️, Cœur ♥️)
VALEURS_CARTES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
ENSEIGNES_ORDRE = ['♠', '♣', '♦', '♥️']

DISPOSITION_52_CARTES = [f"{v}{e}" for e in ENSEIGNES_ORDRE for v in VALEURS_CARTES]

dernieres_stats = {}

# ------------------------------------------------------------------
# RECHERCHE D'HISTORIQUE (TELETHON)
# ------------------------------------------------------------------
async def obtenir_historique_jeu(numero_jeu, limite=1):
    query = f"#N{numero_jeu}."
    async for message in client.iter_messages(CANAL_SOURCE, search=query, limit=limite):
        if message.text:
            return message.text
    return None

# ------------------------------------------------------------------
# ÉCOUTEUR DU CANAL STATISTIQUES (Telethon)
# ------------------------------------------------------------------
client = TelegramClient('session_stats', API_ID, API_HASH)

def extraire_cartes(texte):
    # Capture la valeur (10, A, Q, 4...) et le symbole de couleur de manière ultra flexible
    return re.findall(r'(10|[2-9]|A|J|Q|K)\s*([♠♣♦♥️\u2660-\u2667\uFE0F]+)', texte)

@client.on(events.NewMessage(chats=CANAL_SOURCE))
async def ecouter_canal(event):
    global dernieres_stats
    texte = event.message.text

    match_jeu = re.search(r'#N(\d+)', texte)
    num_jeu = int(match_jeu.group(1)) if match_jeu else None

    cartes_trouvees = extraire_cartes(texte)

    if num_jeu and cartes_trouvees:
        dernieres_stats = {
            'jeu': num_jeu,
            'cartes': cartes_trouvees,
            'texte': texte
        }
        print(f"[STATS INTERCEPTÉES] Jeu #{num_jeu} reçu | Cartes : {cartes_trouvees}")

def lancer_scrapper():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client.start()
    client.run_until_disconnected()

# ------------------------------------------------------------------
# BOUCLE D'ENVOI DES PRÉDICTIONS
# ------------------------------------------------------------------
def boucle_envoi_automatique():
    deja_envoye = set()

    while True:
        try:
            if dernieres_stats and 'jeu' in dernieres_stats:
                num_jeu_actuel = dernieres_stats['jeu']

                if num_jeu_actuel % 4 == 0 and num_jeu_actuel not in deja_envoye:
                    deja_envoye.add(num_jeu_actuel)
                    
                    cartes = dernieres_stats.get('cartes', [])
                    if cartes:
                        val_carte, enseigne_carte = cartes[0]
                        
                        # Nettoyage du symbole
                        ens_clean = '♠' if '♠' in enseigne_carte else '♣' if '♣' in enseigne_carte else '♦' if '♦' in enseigne_carte else '♥️'
                        premiere_carte_str = f"{val_carte}{ens_clean}"

                        # Recherche de la position
                        position = 1
                        for idx, c in enumerate(DISPOSITION_52_CARTES):
                            if val_carte in c and ens_clean in c:
                                position = idx + 1
                                break

                        # Historique
                        texte_jeu_historique = asyncio.run_coroutine_threadsafe(
                            obtenir_historique_jeu(position),
                            client.loop
                        ).result(timeout=10)

                        carte_a_jouer = "Non détectée"
                        if texte_jeu_historique:
                            cartes_hist = extraire_cartes(texte_jeu_historique)
                            if cartes_hist:
                                val_h, ens_h = cartes_hist[0]
                                ens_h_clean = '♠' if '♠' in ens_h else '♣' if '♣' in ens_h else '♦' if '♦' in ens_h else '♥️'
                                carte_a_jouer = f"{val_h}{ens_h_clean}"

                        jeu_cible = num_jeu_actuel + 3

                        msg = (
                            f"🚀 **PRÉDICTION BACCARAT**\n\n"
                            f"📊 Jeu Déclencheur : #{num_jeu_actuel}\n"
                            f"🃏 Carte d'origine : {premiere_carte_str} (Position #{position})\n"
                            f"🔍 Carte issue du Jeu #{position} : {carte_a_jouer}\n\n"
                            f"🎯 **À jouer au Jeu #{jeu_cible} : {carte_a_jouer}**"
                        )

                        bot.send_message(CHAT_ID_CIBLE, msg, parse_mode="Markdown")
                        print(f"[PRÉDICTION ENVOYÉE] Jeu {num_jeu_actuel} -> Jeu {jeu_cible}")

            time.sleep(3)
        except Exception as e:
            print(f"Erreur boucle envoi : {e}")
            time.sleep(5)

# ------------------------------------------------------------------
# FLASK & DEMARRAGE
# ------------------------------------------------------------------
@app.route('/')
def home():
    return "Bot Oracle Baccarat actif !"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t_flask = threading.Thread(target=run_flask)
    t_flask.daemon = True
    t_flask.start()

    t_stats = threading.Thread(target=lancer_scrapper)
    t_stats.daemon = True
    t_stats.start()

    t_auto = threading.Thread(target=boucle_envoi_automatique)
    t_auto.daemon = True
    t_auto.start()

    bot.infinity_polling(timeout=10, long_polling_timeout=5)
