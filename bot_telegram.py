import os
import re
import asyncio
import telegram
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# 1. Configuration des identifiants (Variables d'environnement Render)
API_ID = int(os.getenv("API_ID", 36011582))
API_HASH = os.getenv("API_HASH", "1a59e486bbe7867994bae4450a958f7c")
TELEGRAM_SESSION = os.getenv("TELEGRAM_SESSION")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # Ex: -1001234567890

# 2. Initialisation des clients
telegram_bot = telegram.Bot(token=BOT_TOKEN) if BOT_TOKEN else None
telethon_client = TelegramClient(
    StringSession(TELEGRAM_SESSION), API_ID, API_HASH
) if TELEGRAM_SESSION else None

# Dictionnaire mémoire pour suivre les jeux en cours (ex: {"305": "Player"})
pending_predictions = {}

# 3. Regex adaptée au format exact du canal : #N305. ✅7(A♥ 6♣) - 6(6♦ J♥)
RESULT_PATTERN = re.compile(
    r'#N(?P<game>\d+)\.\s*(?P<player_win>✅)?(?P<player_score>\d+)\(.*?\)\s*-\s*(?P<banker_win>✅)?(?P<banker_score>\d+)'
)

# 4. Écouteur de messages Telethon sur le canal source
if telethon_client:
    @telethon_client.on(events.NewMessage(chats='statistika_baccara'))
    async def handle_new_result(event):
        text = event.raw_text
        match = RESULT_PATTERN.search(text)
        
        if not match:
            return  # Message non conforme ignoré

        game_id = match.group('game')
        player_won = bool(match.group('player_win'))  # True si ✅ est côté Joueur
        
        # Validation du jeu s'il est dans la liste des prédictions
        if game_id in pending_predictions:
            prediction = pending_predictions.pop(game_id)
            
            if player_won:
                result_msg = f"🎮 **Jeu #{game_id}**\n✅ **Résultat : GAGNÉ !** (Joueur victorieux)"
            else:
                result_msg = f"🎮 **Jeu #{game_id}**\n❌ **Résultat : PERDU !**"
                
            if telegram_bot and CHANNEL_ID:
                await telegram_bot.send_message(chat_id=CHANNEL_ID, text=result_msg, parse_mode='Markdown')

# 5. Fonction pour publier une nouvelle prédiction (à appeler par votre logique)
async def send_prediction(game_id: str, choice: str = "Player"):
    pending_predictions[game_id] = choice
    msg = f"🔮 **Prédiction Jeu #{game_id}**\n🎯 Mise conseillée : **{choice}**"
    if telegram_bot and CHANNEL_ID:
        await telegram_bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown')
