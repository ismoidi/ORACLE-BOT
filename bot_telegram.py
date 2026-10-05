import re
from telethon import events

# Motif regex adapté au format exact du canal : #N305. ✅7(A♥ 6♣) - 6(6♦ J♥)
RESULT_PATTERN = re.compile(
    r'#N(?P<game>\d+)\.\s*(?P<player_win>✅)?(?P<player_score>\d+)\(.*?\)\s*-\s*(?P<banker_win>✅)?(?P<banker_score>\d+)'
)

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
        
        # Validation : succès si on avait prédit "Player" et que le Joueur a gagné
        if player_won:
            result_msg = f"🎮 **Jeu #{game_id}**\n✅ **Résultat : GAGNÉ !** (Joueur victorieux)"
        else:
            result_msg = f"🎮 **Jeu #{game_id}**\n❌ **Résultat : PERDU !**"
            
        # Envoi de la confirmation sur votre canal
        await telegram_bot.send_message(chat_id=YOUR_CHANNEL_ID, text=result_msg)
