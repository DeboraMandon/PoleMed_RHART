import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import configparser
import getpass

st.image('logo.png', use_column_width=1)
st.title("Calcul des heures des ART")
st.sidebar.subheader("Authentification :")

username = getpass.getuser()

# télécharger les données puis les conserver en cache
@st.cache_data
def load_data():
    df= pd.read_csv("C:/Users"+username+"/Imadis Téléradiologie/INTRANET - IMADIS/QUALITE/7- RHM/15 - DMA/GitHub/data/BDD.csv")
    return df
df = load_data()

def authentication():
    config = configparser.ConfigParser()
    config.read('cred_art.ini')
    mdp = config.get('Credentials', 'mdp_rhm')

    password = st.sidebar.text_input("Mot de passe :", type="password")
    if password == mdp:
        return True
    else:
        return False

def main():
    if authentication():
        st.sidebar.markdown("<p style='color:red'>Application sécurisée</p>", unsafe_allow_html=True)
        st.write("")
        pages= ['🏥 Accueil', '🚀 Chargement des données', '📈 Visualisation', '🧾Horaires des ART - du 26 au 25 comptabilité']
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


        if page == pages[1]:
            st.header("Données :")
            st.write("Les données vont du",df['Date'].iloc[0], "au",df['Date'].iloc[-1], ".")    
            
            if st.checkbox("Afficher les données brutes :", False):
                st.subheader("Visualisation du jeu de données : ")
                st. write("Nombre de lignes et nombre de colonne :", df.shape)
                st.dataframe(df)
                #st.write(df.dtypes)
            st.sidebar.image('logo.png')
            
        if page == pages[2]:
            st.header("Horaires des ART")
            st.sidebar.image('logo.png')
            mois={"janvier":1, "février":2, "mars":3, "avril":4, "mai":5, "juin":6, "juillet":7, 
                "août":8, "septembre":9, "octobre":10, "novembre":11, "décembre":12}
            mois_select=st.selectbox("Choisissez un mois :", list(mois.keys()))
            mois_int = mois[mois_select]
            
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
            mois_filtre = mois_int 
            df_filtre = df[df['Date'].dt.month == mois_filtre]
            
            if not df_filtre.empty:
                st.subheader(f"Durée totale réalisée par ART pour le mois de {mois_select}")
                couleurs_sites = {"St etienne": '#38E446', "Lyon": '#0F095F', "Bordeaux":'#A62A2A', "Rennes":'#E5EA18', 
                                "Marseille": '#33F0FF', "Dijon":'#D7820B', "Clermont":"#99249F", "Brest":'#474C4C'}
                grouped_data = df_filtre.groupby(['Nom_Prénom', 'Site'])['Durée'].sum().reset_index()
                fig1=plt.figure(figsize=(20, 12))
                ax = sns.barplot(x='Nom_Prénom', y='Durée', 
                                 hue='Site', data=grouped_data, 
                                 palette=couleurs_sites, ci=None, width=0.5)
                plt.style.use('seaborn-whitegrid')
                sns.despine()
                for container in ax.containers:
                    ax.bar_label(container)
                plt.grid(True, color='lightgray')
                plt.title(f"Durée totale réalisée par ART pour le mois de {mois_select}.")
                for p in ax.patches:
                    width = p.get_width()
                    height = p.get_height()
                    x, y = p.get_xy()
                plt.xlabel("Nom de l'ART")
                plt.ylabel('Durée totale')
                plt.xticks(rotation=70, ha='right',)
                plt.legend(loc="best")
                st.pyplot(fig1)
                
                st.subheader(f"Durée cumulée réalisée par ART pour le mois de {mois_select}")
                grouped_data['Durée'] = grouped_data.groupby(['Nom_Prénom'])['Durée'].cumsum()
                st.dataframe(grouped_data)
                st.markdown(download_excel(grouped_data), unsafe_allow_html=True)
                        
                st.subheader(f"Total des vacations réalisées par ART pour le mois de {mois_select}")
                site_sel=st.multiselect("Site:", couleurs_sites, default=couleurs_sites)
                grouped_data2 = df_filtre.groupby(['Nom_Prénom', 'Site', 'Date'])['Durée'].sum().reset_index()
                grouped_data_filtr=grouped_data2[grouped_data2['Site'].isin (site_sel)]
                grouped_data_filtr=grouped_data_filtr.sort_values(by='Nom_Prénom', ascending=True)
                st.dataframe(grouped_data_filtr)
                st.markdown(download_excel(grouped_data_filtr), unsafe_allow_html=True)

        if page == pages[3]:
            st.header("Horaires des ART - du 26 au 25 comptabilité")
            st.sidebar.image('logo.png')
            mois={"janvier":1, "février":2, "mars":3, "avril":4, "mai":5, "juin":6, "juillet":7, 
                "août":8, "septembre":9, "octobre":10, "novembre":11, "décembre":12}
            mois_select=st.selectbox("Choisissez un mois :", list(mois.keys()))
            mois_int = mois[mois_select]

            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
            #mois_filtre = mois_int 
            #df_filtre = df[df['Date'].dt.month == mois_filtre]
            #             
            # Obtenir la date actuelle
            date_actuelle = datetime.now()

            # Déterminer le mois précédent
            mois_precedent = date_actuelle.month - 1 if date_actuelle.month > 1 else 12

            # Obtenir l'année correspondante pour le mois précédent
            annee_precedente = date_actuelle.year if date_actuelle.month > 1 else date_actuelle.year - 1

            # Déterminer la date de début (26 du mois précédent)
            date_debut = datetime(annee_precedente, mois_precedent, 26)

            # Déterminer la date de fin (25 du mois sélectionné)
            date_fin = datetime(date_actuelle.year, mois_int, 25)
            df_filtre = df[(df['Date'] >= date_debut) & (df['Date'] <= date_fin)]
            
            if not df_filtre.empty:
                st.subheader(f"Durée totale réalisée par ART du {date_debut.day}/{date_debut.month} au {date_fin.day}/{date_fin.month}")
                couleurs_sites = {"St etienne": '#38E446', "Lyon": '#0F095F', "Bordeaux":'#A62A2A', "Rennes":'#E5EA18', 
                                "Marseille": '#33F0FF', "Dijon":'#D7820B', "Clermont":"#99249F", "Brest":'#474C4C'}
                grouped_data = df_filtre.groupby(['Nom_Prénom', 'Site'])['Durée'].sum().reset_index()
                fig2=plt.figure(figsize=(20, 12))
                ax = sns.barplot(x='Nom_Prénom', y='Durée', 
                                 hue='Site', data=grouped_data, 
                                 palette=couleurs_sites, ci=None, width=0.5)
                plt.style.use('seaborn-whitegrid')
                sns.despine()
                for container in ax.containers:
                    ax.bar_label(container)
                plt.grid(True, color='lightgray')
                plt.title(f"Durée totale réalisée par ART pour le mois de {mois_select}.")
                for p in ax.patches:
                    width = p.get_width()
                    height = p.get_height()
                    x, y = p.get_xy()
                plt.xlabel("Nom de l'ART")
                plt.ylabel('Durée totale')
                plt.xticks(rotation=70, ha='right',)
                plt.legend(loc="best")
                st.pyplot(fig2)
                
                st.subheader(f"Durée cumulée réalisée par ART pour le mois de {mois_select}")
                grouped_data['Durée'] = grouped_data.groupby(['Nom_Prénom'])['Durée'].cumsum()
                st.dataframe(grouped_data)
                st.markdown(download_excel(grouped_data), unsafe_allow_html=True)
                        
                st.subheader(f"Total des vacations réalisées par ART pour le mois de {mois_select}")
                site_sel=st.multiselect("Site:", couleurs_sites, default=couleurs_sites)
                grouped_data2 = df_filtre.groupby(['Nom_Prénom', 'Site', 'Date'])['Durée'].sum().reset_index()
                grouped_data_filtr=grouped_data2[grouped_data2['Site'].isin (site_sel)]
                grouped_data_filtr=grouped_data_filtr.sort_values(by='Nom_Prénom', ascending=True)
                st.dataframe(grouped_data_filtr)
                st.markdown(download_excel(grouped_data_filtr), unsafe_allow_html=True)

            else:
                st.write(f"Aucune donnée disponible pour le mois {mois_select}.")
        
        
    else:
        st.error("Mot de passe incorrect")
 
if __name__ == '__main__':
    main()


