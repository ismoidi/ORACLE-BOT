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
client = TelegramClient(StringSession(STRING_SESSION_KEY), API_ID, API_HASH
