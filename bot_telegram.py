import os
import threading
from datetime import datetime
from flask import Flask
import telebot

# ---------------------------------------------------------
# 1. SERVEUR FLASK POUR GARDER RENDER ACTIF
# ---------------------------------------------------------
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot Telegram actif et opérationnel !"


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


# ---------------------------------------------------------
# 2. CONFIGURATION DU BOT TELEGRAM
# ---------------------------------------------------------
TELEGRAM_TOKEN = "8434603595:AAG5hkLGyXppK805olMcOTGxo0p3E2ATJ80"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

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
  chiffres = [int(c) for c in str(numero_jeu) if c != "0"]

  cartes_detectees = []
  couleurs_detectees = []

  for c in chiffres:
    carte, couleur = determiner_carte_par_position(c)
    cartes_detectees.append(carte)
    couleurs_detectees.append(couleur)

  # Si toutes les cartes sont identiques
  if len(set(cartes_detectees)) == 1:
    return cartes_detectees[0]

  # Si cartes différentes -> division par le nombre de couleurs uniques
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
    bot.reply_to(message, "Veuillez envoyer un numéro de jeu valide (chiffres).")


# ---------------------------------------------------------
# 3. DÉMARRAGE SIMULTANÉ (FLASK + TELEGRAM)
# ---------------------------------------------------------
if __name__ == "__main__":
  # Démarrage de Flask dans un thread séparé
  t = threading.Thread(target=run_flask)
  t.daemon = True
  t.start()

  # Démarrage de la boucle du bot Telegram
  bot.infinity_polling(timeout=10, long_polling_timeout=5)
               
