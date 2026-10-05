import os
import sys
from datetime import datetime
import telebot

# Jeton de votre bot Telegram
TELEGRAM_TOKEN = "8434603595:AAG5hkLGyXppK805olMcOTGxo0p3E2ATJ80"

# Initialisation du bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Suite exacte de 52! (68 chiffres)
SUITE_CHIFFRES = (
    "80658175170943878571660636856403766975289505440883277824000000000000"
)


def determiner_carte_par_position(position):
  enseignes = ["Pique ♠️", "Trèfle ♣️", "Carreau ♦️", "Cœur ♥️"]
  index_reel = (position - 1) % len(SUITE_CHIFFRES)
  chiffre = SUITE_CHIFFRES[index_reel]

  valeur = "10" if chiffre == "0" else chiffre
  enseigne = enseignes[index_reel % 4]

  return f"{valeur} de {enseigne}", enseigne


def appliquer_strategie(numero_jeu):
  # 1. Décomposition des chiffres non nuls
  chiffres = [int(c) for c in str(numero_jeu) if c != "0"]

  cartes_detectees = []
  couleurs_detectees = []

  for c in chiffres:
    carte, couleur = determiner_carte_par_position(c)
    cartes_detectees.append(carte)
    couleurs_detectees.append(couleur)

  # 2. Si toutes les cartes sont identiques
  if len(set(cartes_detectees)) == 1:
    return cartes_detectees[0]

  # 3. Si différentes -> comptage des couleurs et division du jeu initial
  nb_couleurs_uniques = len(set(couleurs_detectees))
  jeu_divise = numero_jeu // nb_couleurs_uniques
  position_finale = ((jeu_divise - 1) % len(SUITE_CHIFFRES)) + 1

  carte_finale, _ = determiner_carte_par_position(position_finale)
  return carte_finale


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message, "🔮 Bot actif ! Envoyez un numéro de jeu (ex: 724, 756)."
  )


@bot.message_handler(func=lambda message: True)
def traiter_message(message):
  texte = message.text.strip()
  if texte.isdigit():
    numero_jeu = int(texte)
    carte = appliquer_strategie(numero_jeu)
    bot.reply_to(
        message, f"🎯 Pour le jeu {numero_jeu}, la carte à jouer est : {carte}"
    )
  else:
    bot.reply_to(
        message, "Veuillez envoyer un numéro de jeu valide (uniquement chiffres)."
    )


if __name__ == "__main__":
  print("Démarrage du bot Telegram...")
  bot.infinity_polling(timeout=10, long_polling_timeout=5)
    
