import sqlite3
import pandas as pd
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Mini CRM", page_icon="📊", layout="wide"
)

DB_NAME = "crm_database.db"


# --- GESTION DE LA BASE DE DONNÉES (SQLite) ---
def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            entreprise TEXT,
            email TEXT,
            telephone TEXT,
            statut TEXT,
            notes TEXT,
            date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
  conn.commit()
  conn.close()


def ajouter_prospect(nom, entreprise, email, telephone, statut, notes):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO prospects (nom, entreprise, email, telephone, statut, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
      (nom, entreprise, email, telephone, statut, notes),
  )
  conn.commit()
  conn.close()


def charger_prospects():
  conn = sqlite3.connect(DB_NAME)
  df = pd.read_sql_query("SELECT * FROM prospects", conn)
  conn.close()
  return df


def modifier_prospect(prospect_id, statut, notes):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      """
        UPDATE prospects SET statut = ?, notes = ? WHERE id = ?
    """,
      (statut, notes, prospect_id),
  )
  conn.commit()
  conn.close()


def supprimer_prospect(prospect_id):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM prospects WHERE id = ?", (prospect_id,))
  conn.commit()
  conn.close()


# Initialisation de la base de données au lancement
init_db()

# --- INTERFACE UTILISATEUR (STREAMLIT) ---
st.title("📊 Mini CRM - Gestion des Prospects")
st.markdown("Gérez vos prospects, suivez leur statut et organisez vos ventes.")

# --- BARRE LATÉRALE (NAVIGATION & AJOUT) ---
st.sidebar.header("Navigation")
menu = st.sidebar.selectbox(
    "Choisir une option",
    [
        "Tableau de bord",
        "Liste des prospects",
        "Ajouter un prospect",
        "Modifier / Supprimer",
    ],
)

statuts_possibles = [
    "Nouveau",
    "Contacté",
    "Qualifié",
    "Gagné (Client)",
    "Perdu",
]

# --- 1. TABLEAU DE BORD ---
if menu == "Tableau de bord":
  st.subheader("📈 Tableau de bord & Statistiques")
  df = charger_prospects()

  if df.empty:
    st.info(
        "Aucun prospect pour le moment. Utilisez l'onglet 'Ajouter un prospect'"
        " pour commencer."
    )
  else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Prospects", len(df))
    gagnes = len(df[df["statut"] == "Gagné (Client)"])
    col2.metric("Clients Gagnés", gagnes)
    taux_conversion = (gagnes / len(df)) * 100 if len(df) > 0 else 0
    col3.metric("Taux de conversion", f"{taux_conversion:.1f}%")

    st.markdown("---")
    st.subheader("Répartition par Statut")
    statut_counts = df["statut"].value_counts()
    st.bar_chart(statut_counts)

# --- 2. LISTE DES PROSPECTS ---
elif menu == "Liste des prospects":
  st.subheader("📋 Annuaire des prospects")
  df = charger_prospects()

  if df.empty:
    st.info("Aucun prospect enregistré.")
  else:
    # Filtre par statut
    filtre_statut = st.selectbox(
        "Filtrer par statut", ["Tous"] + statuts_possibles
    )
    if filtre_statut != "Tous":
      df = df[df["statut"] == filtre_statut]

    # Recherche textuelle
    recherche = st.text_input(
        "🔍 Rechercher (Nom ou Entreprise)", ""
    ).lower()
    if recherche:
      df = df[
          df["nom"].str.lower().str.contains(recherche, na=False)
          | df["entreprise"].str.lower().str.contains(recherche, na=False)
      ]

    st.dataframe(df, use_container_width=True)

# --- 3. AJOUTER UN PROSPECT ---
elif menu == "Ajouter un prospect":
  st.subheader("➕ Ajouter un nouveau prospect")

  with st.form("form_ajout"):
    col1, col2 = st.columns(2)
    with col1:
      nom = st.text_input("Nom complet *")
      entreprise = st.text_input("Entreprise")
      email = st.text_input("Email")
    with col2:
      telephone = st.text_input("Téléphone")
      statut = st.selectbox("Statut", statuts_possibles)

    notes = st.text_area("Notes / Commentaires")

    submit = st.form_submit_button("Enregistrer le prospect")

    if submit:
      if nom.strip() == "":
        st.error("Le champ 'Nom complet' est obligatoire.")
      else:
        ajouter_prospect(nom, entreprise, email, telephone, statut, notes)
        st.success(f"Le prospect **{nom}** a bien été ajouté !")

# --- 4. MODIFIER / SUPPRIMER ---
elif menu == "Modifier / Supprimer":
  st.subheader("✏️ Modifier ou Supprimer un prospect")
  df = charger_prospects()

  if df.empty:
    st.info("Aucun prospect à modifier.")
  else:
    # Sélection du prospect via un dictionnaire ID -> Nom (Entreprise)
    prospect_dict = {
        f"{row['id']} - {row['nom']} ({row['entreprise']})": row["id"]
        for index, row in df.iterrows()
    }
    selection = st.selectbox(
        "Sélectionner un prospect à modifier", list(prospect_dict.keys())
    )

    if selection:
      prospect_id = prospect_dict[selection]
      # Récupérer les données actuelles du prospect
      prospect_data = df[df["id"] == prospect_id].iloc[0]

      with st.form("form_modif"):
        nouveau_statut = st.selectbox(
            "Statut",
            statuts_possibles,
            index=statuts_possibles.index(prospect_data["statut"])
            if prospect_data["statut"] in statuts_possibles
            else 0,
        )
        nouvelles_notes = st.text_area(
            "Notes", value=str(prospect_data["notes"])
        )

        col_m1, col_m2 = st.columns(2)
        update_btn = col_m1.form_submit_button("Mettre à jour")
        delete_btn = col_m2.form_submit_button("Supprimer ce prospect")

        if update_btn:
          modifier_prospect(prospect_id, nouveau_statut, nouvelles_notes)
          st.success("Prospect mis à jour avec succès !")
          st.rerun()

        if delete_btn:
          supprimer_prospect(prospect_id)
          st.warning("Prospect supprimé.")
          st.rerun()