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

SUITE_CHIFFRES = "80658175170943878571660636856403766975289505440883277824"

# Stockage global des statistiques extraites du canal
dernieres_stats = {}

# ------------------------------------------------------------------
# RECHERCHE D'HISTORIQUE (TELETHON)
# ------------------------------------------------------------------
async def obtenir_historique_jeu(numero_jeu, limite=5):
    """
    Recherche les 'limite' derniers résultats du jeu spécifié dans le canal.
    """
    query = f"#N{numero_jeu}"
    messages_trouves = []
    
    async for message in client.iter_messages(CANAL_SOURCE, search=query, limit=limite):
        if message.text:
            messages_trouves.append(message.text)
            
    return messages_trouves

# ------------------------------------------------------------------
# ÉCOUTEUR DU CANAL STATISTIQUES (Telethon)
# ------------------------------------------------------------------
client = TelegramClient('session_stats', API_ID, API_HASH)

@client.on(events.NewMessage(chats=CANAL_SOURCE))
async def ecouter_canal(event):
    global dernieres_stats
    texte = event.message.text

    match_jeu = re.search(r'#N(\d+)', texte)
    num_jeu = match_jeu.group(1) if match_jeu else None

    enseignes = re.findall(r'[♣️♦️♠️️♥️]', texte)

    dernieres_stats = {
        'jeu': num_jeu,
        'enseignes': enseignes,
        'texte': texte
    }
    print(f"[STATS INTERCEPTÉES] Jeu #{num_jeu} reçu depuis {CANAL_SOURCE}")

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
            maintenant = datetime.now(timezone.utc) + timedelta(hours=1) # Fuseau horaire Niger (UTC+1)
            minute_actuelle = maintenant.minute
            seconde_actuelle = maintenant.second

            # Synchronisation sur l'intervalle de 4 minutes
            if minute_actuelle % 4 == 1 and seconde_actuelle < 5:
                # Calcul de l'heure d'envoi théorique
                heure_envoi_dt = maintenant - timedelta(seconds=seconde_actuelle)
                
                # Calcul du jeu à venir (+3 minutes de décalage)
                heure_cible_dt = heure_envoi_dt + timedelta(minutes=3)
                
                identifiant_message = heure_envoi_dt.strftime("%H:%M")

                if identifiant_message not in deja_envoye:
                    m = heure_cible_dt.minute
                    h = heure_cible_dt.hour
                    num_jeu = (h * 60 + m) % 1000

                    heure_envoi_str = heure_envoi_dt.strftime("%H:%M")

                    # Exemple simple de sélection de carte
                    index_chiffre = (h + m) % len(SUITE_CHIFFRES)
                    valeur_chiffre = int(SUITE_CHIFFRES[index_chiffre])

                    if valeur_chiffre % 2 == 0:
                        carte_a_jouer = "Cœur ♥️"
                    else:
                        carte_a_jouer = "Trèfle ♣️"

                    msg = (
                        f"🚀 **PRÉDICTION AUTOMATIQUE**\n"
                        f"🎮 Jeu à venir : {num_jeu}\n"
                        f"⏰ Heure d'envoi : {heure_envoi_str} (3 min avant)\n"
                        f"🎯 Carte à jouer : {carte_a_jouer}"
                    )

                    bot.send_message(CHAT_ID_CIBLE, msg, parse_mode="Markdown")
                    print(f"[ENVOI UNIQUE REUSSI] {identifiant_message} -> Jeu {num_jeu}")

                    deja_envoye.add(identifiant_message)
                    
                    if len(deja_envoye) > 100:
                        deja_envoye.clear()

            time.sleep(2)
        except Exception as e:
            print(f"Erreur dans la boucle d'envoi : {e}")
            time.sleep(5)

# ------------------------------------------------------------------
# SERVEUR WEB FLASK (Pour garder Render actif)
# ------------------------------------------------------------------
@app.route('/')
def home():
    return "Bot Oracle Baccarat actif !"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ------------------------------------------------------------------
# DÉMARRAGE DU PROGRAMME
# ------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Serveur Web Flask (gardé en tâche de fond pour Render)
    t_flask = threading.Thread(target=run_flask)
    t_flask.daemon = True
    t_flask.start()

    # 2. Scrapper Telethon (lit les stats du canal source en continu)
    t_stats = threading.Thread(target=lancer_scrapper)
    t_stats.daemon = True
    t_stats.start()

    # 3. Boucle d'envoi unique des prédictions
    t_auto = threading.Thread(target=boucle_envoi_automatique)
    t_auto.daemon = True
    t_auto.start()

    # 4. Polling Telegram (TOUJOURS EN DERNIER)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
