import os
import re
import time
import asyncio
import threading
from flask import Flask
import telebot
from telethon import TelegramClient
from telethon.sessions import StringSession

# ==========================================
# CONFIGURATION DES IDENTIFIANTS & TOKENS
# ==========================================
API_ID = 36011582
API_HASH = "1a59e486bbe7867994bae4450a958f7c"
BOT_TOKEN = "8434603595:AAEtNoqtct5sH-0erJFxkhUQAqrVRuzPXvk"

# Récupération de la session Telethon depuis les variables d'environnement
STRING_SESSION_KEY = os.environ.get("TELEGRAM_SESSION", "")

# Identifiants des canaux Telegram
SOURCE_CHANNEL = "@baccarat_source_channel"  # Remplacez par le nom/ID de votre canal source
CHAT_ID_CIBLE = -1001234567890             # Remplacez par l'ID de votre canal de prédictions

# Table des 52 cartes (Disposition)
DISPOSITION_52_CARTES = [
    "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
    "A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
    "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
    "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣"
]

# Initialisation des instances Telegram
bot = telebot.TeleBot(BOT_TOKEN)
client = TelegramClient(StringSession(STRING_SESSION_KEY), API_ID, API_HASH)

# Variables globales de stockage des données
dernieres_stats = {}
deja_envoye = set()

# ==========================================
# EXTRACTION DES CARTES ET FONCTIONS UTILES
# ==========================================
def extraire_cartes(texte):
    """
    Extrait les cartes du texte du message.
    """
    # Recherche du motif des cartes dans le message
    pattern = r'([2-9]|10|[JQKA])\s*([♠♥♦♣])'
    matches = re.findall(pattern, texte)
    return matches

async def obtenir_historique_jeu(position):
    """
    Recherche un jeu historique correspondant à la position.
    """
    try:
        async for message in client.iter_messages(SOURCE_CHANNEL, limit=50):
            if message.text and f"Position #{position}" in message.text:
                return message.text
    except Exception as e:
        print(f"Erreur lors de la recherche d'historique : {e}", flush=True)
    return None

# ==========================================
# SCRAPPER TELETHON (ÉCOUTE DU CANAL SOURCE)
# ==========================================
def lancer_scrapper():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    @client.on(telebot.util.CustomRequest('newMessage'))
    async def handler(event):
        global dernieres_stats
        # Traitement des messages entrant dans le canal source
        pass

    print("[TELETHON] Démarrage du client...", flush=True)
    client.start()
    print("[TELETHON] Connexion établie et écoute active !", flush=True)
    client.run_until_disconnected()

# ==========================================
# BOUCLE D'ENVOI DES PRÉDICTIONS
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
                        
                        
