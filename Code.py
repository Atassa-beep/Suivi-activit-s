# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 12:33:23 2026

@author: yi
"""
import streamlit as st
import pandas as pd
from datetime import date

# 1. Configuration de la page
st.set_page_config(page_title="Suivi-Évaluation d'Activités", layout="wide")

st.title("📊 Outil de Suivi et de Pilotage des Activités (Collaboratif)")
st.write("Connexion Cloud directe via flux CSV - Version Haute Compatibilité.")

# 2. CONFIGURATION DE VOTRE LIEN GOOGLE SHEETS PUBLIÉ EN CSV
# Ton vrai lien est intégré ici directement
URL_CSV_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTsQyWKfiCsTqYAp0_LgcvhFvofH7RU_hyipDSCR4j0kMOB1MWFzemo-A7PKUNgsTgOZYx1WbYoFGiB/pub?output=csv"

# Chargement sécurisé des données
@st.cache_data(ttl=5)  # Rafraîchit les données toutes les 5 secondes
def charger_donnees(url):
    try:
        df = pd.read_csv(url)
        # S'assurer que les colonnes obligatoires existent si la feuille est neuve
        champs_obligatoires = ["Code Activité", "Projet", "Composante", "Activité", "Responsable", 
                               "Date Prévue", "Date Réalisée", "Statut Actuel", "Avancement (%)", 
                               "Budget Prévu (FCFA)", "Lieu", "Bénéficiaires", "Date de Fin", "Observations", "Date Saisie"]
        if df.empty:
            return pd.DataFrame(columns=champs_obligatoires)
        return df
    except Exception as e:
        return pd.DataFrame()

donnees = charger_donnees(URL_CSV_GOOGLE_SHEETS)

# Initialisation de la mémoire temporaire pour la session Streamlit
if "double_stockage" not in st.session_state:
    st.session_state["double_stockage"] = donnees
else:
    if not donnees.empty and len(donnees) > len(st.session_state["double_stockage"]):
        st.session_state["double_stockage"] = donnees

donnees_locales = st.session_state["double_stockage"]

if "id_en_cours_modification" not in st.session_state:
    st.session_state["id_en_cours_modification"] = None

# Listes d'options pour le formulaire
liste_composantes = ["Sensibilisation", "Formation", "VBG", "Agroécologie", "Autres"]
liste_statuts = ["À faire", "En cours", "Bloqué", "Terminé"]

# Valeurs par défaut
def_valeurs = {
    "Projet": "", "Composante": "Sensibilisation", "Activité": "", "Responsable": "",
    "Date Prévue": date.today(), "Date Réalisée": date.today(), "Statut Actuel": "À faire",
    "Avancement": 0, "Budget": 0.0, "Lieu": "", "Bénéficiaires": 0, "Date de Fin": date.today(), "Observations": ""
}

# Si modification active
if st.session_state["id_en_cours_modification"] is not None and not donnees_locales.empty:
    code_modif = st.session_state["id_en_cours_modification"]
    ligne = donnees_locales[donnees_locales["Code Activité"] == code_modif]
    if not ligne.empty:
        def_valeurs["Projet"] = str(ligne.iloc[0]["Projet"])
        def_valeurs["Composante"] = str(ligne.iloc[0]["Composante"])
        def_valeurs["Activité"] = str(ligne.iloc[0]["Activité"])
        def_valeurs["Responsable"] = str(ligne.iloc[0]["Responsable"])
        def_valeurs["Date Prévue"] = pd.to_datetime(ligne.iloc[0]["Date Prévue"]).date()
        def_valeurs["Date Réalisée"] = pd.to_datetime(ligne.iloc[0]["Date Réalisée"]).date() if pd.notna(ligne.iloc[0]["Date Réalisée"]) else date.today()
        def_valeurs["Statut Actuel"] = str(ligne.iloc[0]["Statut Actuel"])
        def_valeurs["Avancement"] = int(ligne.iloc[0]["Avancement (%)"])
        def_valeurs["Budget"] = float(ligne.iloc[0]["Budget Prévu (FCFA)"])
        def_valeurs["Lieu"] = str(ligne.iloc[0]["Lieu"])
        def_valeurs["Bénéficiaires"] = int(ligne.iloc[0]["Bénéficiaires"])
        def_valeurs["Date de Fin"] = pd.to_datetime(ligne.iloc[0]["Date de Fin"]).date()
        def_valeurs["Observations"] = str(ligne.iloc[0]["Observations"]) if pd.notna(ligne.iloc[0]["Observations"]) else ""

# 3. Organisation de l'interface en 2 colonnes
col1, col2 = st.columns([1, 2])

with col1:
    if st.session_state["id_en_cours_modification"] is not None:
        st.subheader(f"✏️ Modifier l'Activité : {st.session_state['id_en_cours_modification']}")
        texte_bouton = "Mettre à jour"
    else:
        st.subheader("➕ Enregistrer une activité")
        texte_bouton = "Enregistrer l'activité"
    
    with st.form("formulaire_suivi", clear_on_submit=False):
        projet = st.text_input("Nom du Projet *", value=def_valeurs["Projet"])
        composante = st.selectbox("Composante *", liste_composantes, index=liste_composantes.index(def_valeurs["Composante"]))
        nom_activite = st.text_area("Description de l'Activité *", value=def_valeurs["Activité"], height=70)
        responsable = st.text_input("Responsable", value=def_valeurs["Responsable"])
        
        c_date1, c_date2 = st.columns(2)
        with c_date1:
            date_prevue = st.date_input("Date Prévue *", value=def_valeurs["Date Prévue"])
            date_fin = st.date_input("Date de Fin *", value=def_valeurs["Date de Fin"])
        with c_date2:
            date_realisee = st.date_input("Date Réalisée (Si applicable)", value=def_valeurs["Date Réalisée"])
        
        statut_actuel = st.selectbox("Statut Actuel *", liste_statuts, index=liste_statuts.index(def_valeurs["Statut Actuel"]))
        avancement = st.slider("Taux d'avancement (%)", 0, 100, value=def_valeurs["Avancement"], step=5)
        
        with st.expander("📊 Données complémentaires (Facultatif)"):
            budget = st.number_input("Budget Prévu (FCFA)", min_value=0.0, value=def_valeurs["Budget"], step=5000.0)
            lieu = st.text_input("Lieu de réalisation", value=def_valeurs["Lieu"])
            beneficiaires = st.number_input("Nombre de bénéficiaires cibles", min_value=0, value=def_valeurs["Bénéficiaires"], step=1)
            observations = st.text_area("Observations / Remarques", value=def_valeurs["Observations"], height=60)

        bouton_valider = st.form_submit_button(texte_bouton)
        
        if bouton_valider:
            if projet and nom_activite:
                d_prev = date_prevue.strftime("%Y-%m-%d")
                d_fin = date_fin.strftime("%Y-%m-%d")
                d_real = date_realisee.strftime("%Y-%m-%d")
                
                if st.session_state["id_en_cours_modification"] is not None:
                    code_actuel = st.session_state["id_en_cours_modification"]
                    idx = donnees_locales[donnees_locales["Code Activité"] == code_actuel].index[0]
                    
                    donnees_locales.at[idx, "Projet"] = projet
                    donnees_locales.at[idx, "Composante"] = composante
                    donnees_locales.at[idx, "Activité"] = nom_activite
                    donnees_locales.at[idx, "Responsable"] = responsable if responsable else "Non assigné"
                    donnees_locales.at[idx, "Date Prévue"] = d_prev
                    donnees_locales.at[idx, "Date Réalisée"] = d_real
                    donnees_locales.at[idx, "Statut Actuel"] = statut_actuel
                    donnees_locales.at[idx, "Avancement (%)"] = avancement
                    donnees_locales.at[idx, "Budget Prévu (FCFA)"] = budget
                    donnees_locales.at[idx, "Lieu"] = lieu if lieu else "Non spécifié"
                    donnees_locales.at[idx, "Bénéficiaires"] = beneficiaires
                    donnees_locales.at[idx, "Date de Fin"] = d_fin
                    donnees_locales.at[idx, "Observations"] = observations
                    
                    st.session_state["id_en_cours_modification"] = None
                    st.success("Activité mise à jour localement !")
                else:
                    prefixe = "".join([mot[0].upper() for mot in composante.split()][:2])
                    num = len(donnees_locales) + 1
                    code_auto = f"ACT-{prefixe}-{num:03d}"
                    
                    nouvelle_ligne = {
                        "Code Activité": code_auto, "Projet": projet, "Composante": composante,
                        "Activité": nom_activite, "Responsable": responsable if responsable else "Non assigné",
                        "Date Prévue": d_prev, "Date Réalisée": d_real, "Statut Actuel": statut_actuel,
                        "Avancement (%)": avancement, "Budget Prévu (FCFA)": budget, "Lieu": lieu if lieu else "Non spécifié",
                        "Bénéficiaires": beneficiaires, "Date de Fin": d_fin, "Observations": observations,
                        "Date Saisie": date.today().strftime("%Y-%m-%d")
                    }
                    
                    st.session_state["double_stockage"] = pd.concat([donnees_locales, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
                    st.success(f"Activité ajoutée localement ! Code : {code_auto}")
                st.rerun()
            else:
                st.error("Veuillez remplir les champs obligatoires (*)")

    if st.session_state["id_en_cours_modification"] is not None:
        if st.button("❌ Annuler la modification", use_container_width=True):
            st.session_state["id_en_cours_modification"] = None
            st.rerun()
    else:
        if st.button("🔄 Vider / Relancer le formulaire", use_container_width=True):
            st.rerun()

# --- COLONNE DROITE : AFFICHAGE & GRAPHIQUES ---
with col2:
    st.subheader("📋 Tableau de Suivi-Évaluation")
    
    if donnees_locales.empty:
        st.info("Aucune donnée enregistrée pour le moment. Remplissez le formulaire.")
    else:
        donnees_affichage = donnees_locales.drop(columns=["Date Saisie"], errors="ignore")
        donnees_affichage.insert(0, "Sélection", False)
        
        evenement_selection = st.data_editor(
            donnees_affichage, 
            use_container_width=True, 
            hide_index=True,
            disabled=[col for col in donnees_affichage.columns if col != "Sélection"]
        )
        
        lignes_cochees = evenement_selection[evenement_selection["Sélection"] == True]
        
        if not lignes_cochees.empty:
            code_choisi = lignes_cochees.iloc[0]["Code Activité"]
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button("✏️ Modifier cette activité", use_container_width=True):
                    st.session_state["id_en_cours_modification"] = code_choisi
                    st.rerun()
            with c_b2:
                if st.button("🗑️ Supprimer définitivement", use_container_width=True):
                    st.session_state["double_stockage"] = donnees_locales[donnees_locales["Code Activité"] != code_choisi]
                    if st.session_state["id_en_cours_modification"] == code_choisi:
                        st.session_state["id_en_cours_modification"] = None
                    st.success("Activité retirée.")
                    st.rerun()
        
        # --- SECTION VISUALISATION ---
        st.markdown("---")
        st.subheader("📊 Analyses Statistiques Directes")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**Répartition par Composante**")
            st.bar_chart(donnees_locales["Composante"].value_counts())
            
        with col_g2:
            st.markdown("**Situation par Statut Actuel**")
            st.bar_chart(donnees_locales["Statut Actuel"].value_counts())
            
        st.markdown("### 📌 Indicateurs Clés Centraux")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Activités", len(donnees_locales))
        m2.metric("Bénéficiaires Globaux", int(pd.to_numeric(donnees_locales["Bénéficiaires"], errors="coerce").sum()))
        m3.metric("Budget Global Mobilisé", f"{pd.to_numeric(donnees_locales['Budget Prévu (FCFA)'], errors='coerce').sum():,.0f} FCFA")