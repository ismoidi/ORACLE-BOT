
import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from flask import Flask
import telebot
import asyncio
from telethon import TelegramClient, events

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
TELEGRAM_TOKEN = "8434603595:AAG5hkLGyXppK805olMcOTGxo0p3E2ATJ80"
CHAT_ID_CIBLE = "-1003983624932"

# Identifiants API (my.telegram.org)
API_ID = 36011582
API_HASH = "1a59e486bbe7867994bae4450a958f7c"
CANAL_SOURCE = "jokerwcbnn11280"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

SUITE_CHIFFRES = "80658175170943878571660636856403766975289505440883277824000000000000"

# Variable globale pour stocker les statistiques interceptées
dernieres_stats = {}

# ---------------------------------------------------------
# ÉCOUTEUR DU CANAL STATISTIQUES (Telethon)
# ---------------------------------------------------------
def lancer_scrapper():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    client = TelegramClient('session_stats', API_ID, API_HASH)

    @client.on(events.NewMessage(chats=CANAL_SOURCE))
    async def ecouter_canal(event):
        global dernieres_stats
        texte = event.message.text

        match_jeu = re.search(r'#N(\d+)', texte)
        num_jeu = match_jeu.group(1) if match_jeu else None

        enseignes = re.findall(r'[♣️♦️♠️♥️]', texte)

        dernieres_stats = {
            'jeu': num_jeu,
            'enseignes': enseignes,
            'texte': texte
        }
        print(f"[STATS INTERCEPTÉES] Jeu #{num_jeu} reçu depuis {CANAL_SOURCE} !")

    client.start()
    client.run_until_disconnected()

# ---------------------------------------------------------
# STRATÉGIE MATHÉMATIQUE
# ---------------------------------------------------------
def determiner_carte_par_position(position):
    enseignes = ["Pique ♠️", "Trèfle ♣️", "Carreau ♦️", "Cœur ♥️"]
    index_reel = (position - 1) % len(SUITE_CHIFFRES)
    chiffre = SUITE_CHIFFRES[index_reel]
    
    valeur = "10" if chiffre == '0' else chiffre
    enseigne = enseignes[index_reel % 4]
    
    return f"{valeur} de {enseigne}", enseigne

def appliquer_strategie(numero_jeu):
    global dernieres_stats
    
    if dernieres_stats and dernieres_stats.get('enseignes'):
        print(f"[LOG] Utilisation des dernières stats interceptées : {dernieres_stats['enseignes']}")

    chiffres = [int(c) for c in str(numero_jeu) if c != '0']
    
    cartes_detectees = []
    couleurs_detectees = []
    
    for c in chiffres:
        carte, couleur = determiner_carte_par_position(c)
        cartes_detectees.append(carte)
        couleurs_detectees.append(couleur)
        
    if len(set(cartes_detectees)) == 1:
        return cartes_detectees[0]
        
    nb_couleurs_uniques = len(set(couleurs_detectees))
    jeu_divise = numero_jeu // nb_couleurs_uniques
    position_finale = ((jeu_divise - 1) % len(SUITE_CHIFFRES)) + 1
    
    carte_finale, _ = determiner_carte_par_position(position_finale)
    return carte_finale

def extraire_enseigne_seule(carte_complete):
    if " de " in carte_complete:
        return carte_complete.split(" de ")[1]
    return carte_complete

# ---------------------------------------------------------
# CALCUL HEURE NIGER (UTC+1) ET ENVOI UNIQUE
# ---------------------------------------------------------
def calculer_jeu_actuel_niger():
    tz_niger = timezone(timedelta(hours=1))
    maintenant = datetime.now(tz_niger)
    
    heure = maintenant.hour
    minute = maintenant.minute
    
    minutes_depuis_01h = ((heure - 1) % 24) * 60 + minute
    jeu_actuel = minutes_depuis_01h + 1
    
    return jeu_actuel, maintenant

def boucle_envoi_automatique():
    dernier_jeu_envoye = None
    
    while True:
        jeu_actuel, heure_niger = calculer_jeu_actuel_niger()
        jeu_dans_3min = ((jeu_actuel + 3 - 1) % 1440) + 1
        
        if jeu_dans_3min % 4 == 0 and jeu_dans_3min != dernier_jeu_envoye:
            carte_complete = appliquer_strategie(jeu_dans_3min)
            enseigne_seule = extraire_enseigne_seule(carte_complete)
            
            jeu_affiche = jeu_dans_3min - 1 if jeu_dans_3min > 1 else 1440
            
            message = (
                f"🚀 **PRÉDICTION AUTOMATIQUE**\n"
                f"🎮 **Jeu à venir :** {jeu_affiche}\n"
                f"⏰ **Heure d'envoi :** {heure_niger.strftime('%H:%M')} (3 min avant)\n"
                f"🎯 **Carte à jouer :** {enseigne_seule}"
            )
            
            try:
                bot.send_message(CHAT_ID_CIBLE, message, parse_mode="Markdown")
                dernier_jeu_envoye = jeu_dans_3min
            except Exception as e:
                print(f"Erreur d'envoi : {e}")
                
        time.sleep(10)

# ---------------------------------------------------------
# SERVEUR FLASK & DÉMARRAGE
# ---------------------------------------------------------
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
