def boucle_envoi_automatique():
  dernier_jeu_envoye = None

  while True:
    jeu_actuel, heure_niger = calculer_jeu_actuel_niger()

    # Le jeu divisible par 4 ciblé a lieu dans 3 minutes
    # À 17:33 (Jeu 994), le jeu dans 3 minutes est le Jeu 996 (divisible par 4)
    jeu_cible_div4 = (((jeu_actuel + 2) - 1) % 1440) + 1

    if jeu_cible_div4 % 4 == 0 and jeu_cible_div4 != dernier_jeu_envoye:
      carte_complete = appliquer_strategie(jeu_cible_div4)
      enseigne_seule = extraire_enseigne_seule(carte_complete)

      # Numéro du jeu affiché : le jeu qui précède (ex: 995 pour le jeu 996)
      jeu_affiche = jeu_cible_div4 - 1 if jeu_cible_div4 > 1 else 1440

      message = (
          f"🚀 **PRÉDICTION AUTOMATIQUE**\n"
          f"🎮 **Jeu à venir :** {jeu_affiche}\n"
          f"⏰ **Heure d'envoi :** {heure_niger.strftime('%H:%M')} (3 min"
          " avant)\n"
          f"🎯 **Carte à jouer :** {enseigne_seule}"
      )

      try:
        if CHAT_ID_CIBLE != "VOTRE_CHAT_ID_ICI":
          bot.send_message(CHAT_ID_CIBLE, message, parse_mode="Markdown")
          print(
              f"[{heure_niger.strftime('%H:%M:%S')}] Message envoyé pour le"
              f" jeu {jeu_affiche}"
          )
          dernier_jeu_envoye = jeu_cible_div4
      except Exception as e:
        print(f"Erreur d'envoi : {e}")

    time.sleep(10)
      
