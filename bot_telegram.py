import logging
import itertools
import asyncio
from collections import Counter
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration des journaux d'activité
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Votre Token secret vérifié avec le O majuscule final
TOKEN = "8434603595:AAG5hkLGyXppK805olMcOTGxoOp3E2ATJ8O"

TABLE_EXTRACTION = {
    1: 8, 2: 6, 3: 1, 4: 3, 5: 7, 6: 6, 7: 2, 8: 4, 9: 6, 10: 7,
    11: 9, 12: 5, 13: 1, 14: 5, 15: 1, 16: 1, 17: 3, 18: 2, 19: 6, 20: 5,
    21: 0, 22: 6, 23: 6, 24: 3, 25: 3, 26: 2, 27: 3, 28: 1, 29: 2, 30: 4,
    31: 3, 32: 4, 33: 1, 34: 0, 35: 3, 36: 2, 37: 2, 38: 3, 39: 6, 40: 1,
    41: 4, 42: 5, 43: 5, 44: 1, 45: 0, 46: 4, 47: 8, 48: 0, 49: 5, 50: 1,
    51: 5, 52: 0, 53: 1, 54: 6, 55: 2, 56: 4, 57: 0, 58: 0, 59: 0, 60: 0,
    61: 0, 62: 0, 63: 0, 64: 0, 65: 0, 66: 0
}
SUITE_CHIFFRES = "861376246795151132650663323124341032236145510480515016240000000000"

def determiner_carte_par_ordre_absolu(index_jeu):
    if not SUITE_CHIFFRES or index_jeu <= 0: return None
    enseignes = ["Pique ♠️", "Trèfle ♣️", "Carreau ♦️", "Cœur ♥️"]
    index_chiffre = (index_jeu - 1) % len(SUITE_CHIFFRES)
    chiffre_extrait = SUITE_CHIFFRES[index_chiffre]
    enseigne_actuelle = enseignes[index_chiffre % 4]
    valeur_carte = "10" if chiffre_extrait == '0' else chiffre_extrait
    return f"{valeur_carte} de {enseigne_actuelle}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔮 **Oracle Bot Actif !**\nEnvoyez-moi un numéro de tour (ex: 148) pour obtenir sa carte fixe.")

async def analyser_tour_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte_recu = update.message.text.strip()
    if not texte_recu.isdigit():
        await update.message.reply_text("⚠️ Veuillez envoyer uniquement des chiffres (le numéro du tour).")
        return
        
    prochain_tour = int(texte_recu)
    chiffres_tour = [int(c) for c in str(prochain_tour) if c != '0']
    
    if len(chiffres_tour) < 2: paires = [(chiffres_tour, chiffres_tour)]
    else: paires = list(itertools.combinations(chiffres_tour, 2))
    
    positions_traitees = set()
    for c1, c2 in paires:
        debut, fin = min(c1, c2), max(c1, c2)
        for pos in range(debut, fin + 1): positions_traitees.add(pos)
        
    cartes_trouvees = []
    for pos in sorted(positions_traitees):
        if pos in TABLE_EXTRACTION:
            carte = determiner_carte_par_ordre_absolu(TABLE_EXTRACTION[pos])
            if carte: cartes_trouvees.append(carte)
            
    if cartes_trouvees:
        compteur = Counter(cartes_trouvees)
        gagnant = compteur.most_common(1)
        if gagnant:
            res_carte, nb = gagnant[0]
            await update.message.reply_text(f"🎯 Tour {prochain_tour} → 🃏 **{res_carte}**")
        else:
            await update.message.reply_text("🎯 Aucun résultat trouvé pour ce tour.")
    else:
        await update.message.reply_text("🎯 Aucun résultat trouvé pour ce tour.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyser_tour_telegram))
    print("🤖 Bot Telegram en cours d'exécution...")
    app.run_polling()

if __name__ == '__main__':
    main()
