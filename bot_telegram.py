import os
import threading
import time
from datetime import datetime, timedelta, timezone
from flask import Flask
import telebot

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
TELEGRAM_TOKEN = "8434603595:AAG5hkLGyXppK805olMcOTGxo0p3E2ATJ80"

# ⚠️ REMPLACEZ CETTE VALEUR PAR L'ID DE VOTRE CANAL OU GROUPE TELEGRAM
# (Exemple: -1001234567890 ou votre ID personnel)
CHAT_ID_CIBLE = "VOTRE_CHAT_ID_ICI"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

SUITE_CHIFFRES = (
    "80658175170943878571660636856403766975289505440883277824000000000000"
)


# ---------------------------------------------------------
# STRATÉGIE MATHÉMATIQUE
# ---------------------------------------------------------
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

  if len(set(cartes_detectees)) == 1:
    return cartes_detectees[0]

  nb_couleurs_uniques = len(set(couleurs_detectees))
  jeu_divise = numero_jeu // nb_couleurs_uniques
  position_finale = ((jeu_divise - 1) % len(SUITE_CHIFFRES)) + 1

  carte_finale, _ = determiner_carte_par_position(position_finale)
  return carte_finale


# ---------------------------------------------------------
# CALCUL HEURE NIGER (UTC+1) ET ENVOI 3 MIN AVANT
# ---------------------------------------------------------
def calculer_jeu_actuel_niger():
  tz_niger = timezone(timedelta(hours=1))
  maintenant = datetime.now(tz_niger)

  heure = maintenant.hour
  minute = maintenant.minute

  # Calcul du jeu actuel (Jeu 1 à 01h00 du matin)
  minutes_depuis_01h = ((heure - 1) % 24) * 60 + minute
  jeu_actuel = minutes_depuis_01h + 1

  return jeu_actuel, maintenant


def boucle_envoi_automatique():
  dernier_jeu_envoye = None

  while True:
    jeu_actuel, heure_niger = calculer_jeu_actuel_niger()

    # Le jeu qui aura lieu dans 3 minutes
    jeu_cible = ((jeu_actuel + 3 - 1) % 1440) + 1

    # Envoi si le jeu cible est divisible par 4
    if jeu_cible % 4 == 0 and jeu_cible != dernier_jeu_envoye:
      carte = appliquer_strategie(jeu_cible)

      message = (
          f"🚀 **PRÉDICTION AUTOMATIQUE**\n"
          f"🎮 **Jeu à venir :** {jeu_cible} (Divisible par 4)\n"
          f"⏰ **Heure d'envoi :** {heure_niger.strftime('%H:%M')} (3 min"
          " avant)\n"
          f"🎯 **Carte à jouer :** {carte}"
      )

      try:
        if CHAT_ID_CIBLE != "VOTRE_CHAT_ID_ICI":
          bot.send_message(CHAT_ID_CIBLE, message, parse_mode="Markdown")
          print(
              f"[{heure_niger.strftime('%H:%M:%S')}] Prédiction envoyée pour"
              f" le jeu {jeu_cible}"
          )
          dernier_jeu_envoye = jeu_cible
      except Exception as e:
        print(f"Erreur lors de l'envoi : {e}")

    time.sleep(10)


# ---------------------------------------------------------
# COMMANDES & SERVEUR FLASK
# ---------------------------------------------------------
@bot.message_handler(commands=["id"])
def get_chat_id(message):
  bot.reply_to(
      message,
      f"L'ID de ce tchat/canal est : `{message.chat.id}`",
      parse_mode="Markdown",
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


@app.route("/")
def home():
  return "Bot Telegram actif (Heure Niger UTC+1 - 3 min anticipation) !"


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
  t_flask = threading.Thread(target=run_flask)
  t_flask.daemon = True
  t_flask.start()

  t_auto = threading.Thread(target=boucle_envoi_automatique)
  t_auto.daemon = True
  t_auto.start()

  bot.infinity_polling(timeout=10, long_polling_timeout=5)
