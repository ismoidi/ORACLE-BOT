def boucle_envoi_automatique():
    deja_envoye = set()

    while True:
        try:
            if dernieres_stats and 'jeu' in dernieres_stats:
                num_jeu_actuel = dernieres_stats['jeu']

                # Déclenchement sur jeu divisible par 4
                if num_jeu_actuel % 4 == 0 and num_jeu_actuel not in deja_envoye:
                    deja_envoye.add(num_jeu_actuel)
                    
                    cartes = dernieres_stats.get('cartes', [])
                    if cartes:
                        # 1. Première carte du jeu divisible par 4
                        val_carte, enseigne_carte = cartes[0]
                        premiere_carte_str = f"{val_carte}{enseigne_carte}"

                        # 2. Position dans la séquence des 52 cartes
                        if premiere_carte_str in DISPOSITION_52_CARTES:
                            position = DISPOSITION_52_CARTES.index(premiere_carte_str) + 1
                        else:
                            position = 1

                        # 3. Recherche de la carte dans le jeu passé correspondant à la position
                        texte_jeu_historique = asyncio.run_coroutine_threadsafe(
                            obtenir_historique_jeu(position),
                            client.loop
                        ).result(timeout=10)

                        carte_a_jouer = "Non détectée"
                        if texte_jeu_historique:
                            cartes_hist = re.findall(r'(\d+|[AJQK])([♣️♦️♠♥️])', texte_jeu_historique)
                            if cartes_hist:
                                val_h, ens_h = cartes_hist[0]
                                carte_a_jouer = f"{val_h}{ens_h}"

                        # 4. Prédiction pour le jeu cible (+3)
                        jeu_cible = num_jeu_actuel + 3

                        msg = (
                            f"🚀 **PRÉDICTION BACCARAT**\n\n"
                            f"📊 Jeu Déclencheur : #{num_jeu_actuel}\n"
                            f"🃏 Carte d'origine : {premiere_carte_str} (Position #{position})\n"
                            f"🔍 Carte du Jeu #{position} : {carte_a_jouer}\n\n"
                            f"🎯 **À jouer au Jeu #{jeu_cible} : {carte_a_jouer}**"
                        )

                        bot.send_message(CHAT_ID_CIBLE, msg, parse_mode="Markdown")
                        print(f"[NOUVELLE PRÉDICTION ENVOYÉE] Jeu {num_jeu_actuel} -> Jeu {jeu_cible}")

            time.sleep(3)
        except Exception as e:
            print(f"Erreur dans la boucle d'envoi : {e}")
            time.sleep(5)
