import os
import re
import time
import asyncio
import threading
from flask import Flask
import telebot
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ==========================================
# CONFIGURATION DES IDENTIFIANTS & TOKENS
# ==========================================
API_ID = 36011582
API_HASH = "1a59e486bbe7867994bae4450a958f7c"
BOT_TOKEN = "8434603595:AAEtNoqtct5sH-0erJFxkhUQAqrVRuzPXvk"

# Variable d'environnement pour la session Telethon
STRING_SESSION_KEY = os.environ.get("TELEGRAM_SESSION", "")

# Identifiants de vos canaux configurés
SOURCE_CHANNEL = "@statistika_baccara"
CHAT_ID_CIBLE = -1003983624932

# Disposition standard des 52 cartes
DISPOSITION_52_CARTES = [
    "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
    "A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
    "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
    "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣"
]

# Initialisation des instances
bot = telebot.TeleBot(BOT_TOKEN)
client = TelegramClient(StringSession(STRING_SESSION_KEY), API_ID, API_HASH)

# Variables globales
dernieres_stats = {}
deja_envoye = set()

# ==========================================
# EXTRACTION & HISTORIQUE
# ==========================================
def extraire_cartes(texte):
    pattern = r'([2-9]|10|[JQKA])\s*([♠♥♦♣])'
    return re.findall(pattern, texte)

async def obtenir_historique_jeu(position):
    try:
        async for message in client.iter_messages(SOURCE_CHANNEL, limit=50):
            if message.text and f"Position #{position}" in message.text:
                return message.text
    except Exception as e:
        print(f"[ERREUR HISTORIQUE] {e}", flush=True)
    return None

# ==========================================
# SCRAPPER TELETHON (SANS BUG DE DÉMARRAGE)
# ==========================================
@client.on(events.NewMessage)
async def handler_message(event):
    global dernieres_stats
    try:
        chat = await event.get_chat()
        chat_username = getattr(chat, 'username', None)
        
        # Vérifie si le message provient bien du canal source configuré
        if chat_username and chat_username.lower() == SOURCE_CHANNEL.replace('@', '').lower():
            if event.text:
                cartes = extraire_cartes(event.text)
                match_jeu = re.search(r'Jeu\s*#?(\d+)', event.text, re.IGNORECASE)
                if match_jeu and cartes:
                    num_jeu = int(match_jeu.group(1))
                    dernieres_stats = {
                        'jeu': num_jeu,
                        'cartes': cartes
                    }
                    print(f"[SCRAPPER] Jeu #{num_jeu} détecté.", flush=True)
    except Exception as e:
        pass

def lancer_scrapper():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        print("[TELETHON] Démarrage du client...", flush=True)
        client.start()
        print("[TELETHON] Connexion établie et écoute active sur @statistika_baccara !", flush=True)
        client.run_until_disconnected()
    except Exception as e:
        print(f"[TELETHON ERREUR] {e}", flush=True)

# ==========================================
# BOUCLE D'ENVOI AUTOMATIQUE
# ==========================================
def boucle_envoi_automatique():
    global deja_envoye
    
    while True:
        try:
            if dernieres_stats and 'jeu' in dernieres_stats:
                num_jeu_actuel = dernieres_stats.get('jeu', 0)
                
                if num_jeu_actuel % 4 == 0 and num_jeu_actuel not in deja_envoye:
                    deja_envoye.add(num_jeu_actuel)
                    
                    cartes = dernieres_stats.get('cartes', [])
                    if cartes:
                        val_carte, enseigne_carte = cartes[0]
                        
                        ens_clean = '♠' if '♠' in enseigne_carte else '♥' if '♥' in enseigne_carte else '♦' if '♦' in enseigne_carte else '♣'
                        premiere_carte_str = f"{val_carte}{ens_clean}"
                        
                        position = 1
                        for idx, c in enumerate(DISPOSITION_52_CARTES):
                            if val_carte in c and ens_clean in c:
                                position = idx + 1
                                break
                        
                        texte_jeu_historique = asyncio.run_coroutine_threadsafe(
                            obtenir_historique_jeu(position),
                            client.loop
                        ).result(timeout=10)
                        
                        carte_a_jouer = "Non détectée"
                        if texte_jeu_historique:
                            cartes_hist = extraire_cartes(texte_jeu_historique)
                            if cartes_hist:
                                val_h, ens_h = cartes_hist[0]
                                ens_h_clean = '♠' if '♠' in ens_h else '♥' if '♥' in ens_h else '♦' if '♦' in ens_h else '♣'
                                carte_a_jouer = f"{val_h}{ens_h_clean}"
                        
                        jeu_cible = num_jeu_actuel + 3
                        
                        msg = (
                            f"🚀 **PRÉDICTION BACCARAT**\n\n"
                            f"📌 Jeu Déclencheur : #{num_jeu_actuel}\n"
                            f"🔍 Carte d'origine : {premiere_carte_str} (Position #{position})\n"
                            f"🎯 Carte issue du Jeu #{position} : {carte_a_jouer}\n\n"
                            f"🎯 **À jouer au Jeu #{jeu_cible} : {carte_a_jouer}**"
                        )
                        
                        bot.send_message(CHAT_ID_CIBLE, msg, parse_mode="Markdown")
                        print(f"[PRÉDICTION ENVOYÉE] Jeu #{num_jeu_actuel} -> Jeu #{jeu_cible}", flush=True)
            
            time.sleep(1)
        except Exception as e:
            print(f"[ERREUR BOUCLE ENVOI] {e}", flush=True)
            time.sleep(3)

# ==========================================
# SERVEUR FLASK (KEEP-ALIVE)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Oracle Baccarat actif !"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# DÉMARRAGE DES THREADS
# ==========================================
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

    while True:
        time.sleep(3600)
