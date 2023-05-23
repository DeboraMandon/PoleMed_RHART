import pandas as pd
import streamlit as st
from datetime import datetime


pages= ['Chargement des données', 'Visualisation']
st.image('logo.png')
st.sidebar.subheader("Choisissez votre page : ")
page=st.sidebar.radio("",pages)
st.sidebar.subheader("")
st.sidebar.subheader("")

def calculate_duration(row):
    date_format = '%d/%m/%Y %H:%M:%S'
    start_date = datetime.strptime(row['Date_début'], date_format)
    end_date = datetime.strptime(row['Date_fin'], date_format)
    duration = end_date - start_date
    duration_in_seconds = duration.total_seconds()
    duration_in_hours = duration_in_seconds / 3600
    return duration_in_hours

if page == pages[0]:
    st.title("RH ART")
    st.sidebar.header("Données :")
    excel_file = st.sidebar.file_uploader("Charger un fichier Excel", type=["xlsx", "xls"])

# Vérifier si un fichier a été chargé
    if excel_file is not None:
        # Charger le fichier Excel dans un DataFrame pandas
        df = pd.read_excel(excel_file, header=None)
        colonnes = ['Date', 'Titre', 'Nom', 'Prenom', 'mail', 'Site', 'Type', 'Date_début', 'Date_fin']
        df.columns = colonnes
        df=df.drop(["Titre", "mail", "Type"], axis=1)
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
        df['Date'] = df['Date'].fillna(method='ffill')
        df['Durée'] = df.apply(calculate_duration, axis=1)
        
        st.write("Les données vont du",df['Date'].max(), "au",df['Date'].min() )
        if st.sidebar.checkbox("Afficher les données brutes :", False):
            st.subheader("Visualisation du jeu de données : ")
            st. write("Nombre de lignes et nombre de colonne :", df.shape)
            st.dataframe(df)
            st.write(df.dtypes)
        
if page == pages[1]:
    st.sidebar