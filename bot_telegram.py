import os
import re
import asyncio
from telethon import TelegramClient, events
import telegram

# Identifiants Telegram depuis les variables d'environnement
API_ID = int(os.getenv("API_ID", 36011582))
API_HASH = os.getenv("API_HASH", "1a59e486bbe7867994bae4450a958f7c")
TELEGRAM_SESSION = os.getenv("TELEGRAM_SESSION")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # Assurez-vous d'avoir cette variable dans Render !

# Initialisation du bot et du client Telethon
telegram_bot = telegram.Bot(token=BOT_TOKEN)
telethon_client = TelegramClient(
    StringSession(TELEGRAM_SESSION), API_ID, API_HASH
) if TELEGRAM_SESSION else None

# Dictionnaire pour stocker les prédictions en attente (jeu_id -> prediction)
pending_predictions = {}

# Expression régulière adaptée au format exact du canal : #N305. ✅7(A♥ 6♣) - 6(6♦ J♥)
RESULT_PATTERN = re.compile(
    r'#N(?P<game>\d+)\.\s*(?P<player_win>✅)?(?P<player_score>\d+)\(.*?\)\s*-\s*(?P<banker_win>✅)?(?P<banker_score>\d+)'
)

if telethon_client:
    @telethon_client.on(events.NewMessage(chats='statistika_baccara'))
    async def handle_new_result(event):
        text = event.raw_text
        match = RESULT_PATTERN.search(text)
        
        if not match:
            return  # Ne correspond pas à un message de résultat

        game_id = match.group('game')
        player_won = bool(match.group('player_win'))  # True si ✅ est présent côté Joueur
        
        # Récupérer la prédiction stockée pour ce numéro de jeu
        if game_id in pending_predictions:
            prediction = pending_predictions.pop(game_id)
            
            if player_won:
                result_msg = f"🎮 **Jeu #{game_id}**\n✅ **Résultat : GAGNÉ !** (Joueur victorieux)"
            else:
                result_msg = f"🎮 **Jeu #{game_id}**\n❌ **Résultat : PERDU !**"
                
            # Envoi de la confirmation sur votre canal
            await telegram_bot.send_message(chat_id=CHANNEL_ID, text=result_msg)
