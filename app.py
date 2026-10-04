import streamlit as st

# Titre de l'application
st.title("🃏 Cartes du joueur + 2 rattrapage")

# Initialisation du numéro du tour à 488
if "numero_tour" not in st.session_state:
    st.session_state["numero_tour"] = 488

# Le symbole unique à afficher (le Trèfle)
symbole = "♣️"

# Bouton pour passer au tour suivant
if st.button("🔄 Rafraîchir les calculs", use_container_width=True):
    st.session_state["numero_tour"] += 1
    st.rerun()

# Affichage épuré demandé : Numéro + Symbole (Exemple : 488 ♣️)
st.success(f"{st.session_state['numero_tour']} {symbole}")
