import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import base64


def authentication():
    password = st.sidebar.text_input("Mot de passe :", type="password")
    if password == "rhm2023!":
        return True
    else:
        return False

def main():
    if authentication():
        st.sidebar.markdown("<p style='color:red'>Application sécurisée</p>", unsafe_allow_html=True)
        st.write("")
        pages= ['🏥 Accueil', '🚀 Chargement des données', '📈 Visualisation']
        st.image('logo.png', use_column_width=1)
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

        def download_excel(data):
            excel_file = "data.xlsx"
            data.to_excel(excel_file, index=False, header=True)
            with open(excel_file, "rb") as f:
                excel_data = f.read()
            b64 = base64.b64encode(excel_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{excel_file}">Télécharger Excel</a>'
            return href

        if page == pages[0]:
            st.title("Calcul des heures des ART")
            st.write("Cette application vous permettra d'obtenir les heures de travail des\n",
                    "une fois les données du planning chargée. Vous pouvez les obtenir depuis\n",
                    "le planning IMADIS dans la section 'Administrateur' puis 'Tour de Garde'.\n",
                    "Ensuite sélectionnez le/les Tour(s) de Garde dont vous souhaitez extraire les informations.\n",
                    "Cliquer sur l'îcone du fichier Excel et sélectionner 'ART' puis 'Générer.")
            st.image("planning.png")
            
        st.sidebar.header("Données :")
        excel_file = st.sidebar.file_uploader("Charger un fichier Excel (dates les plus anciennes)", type=["xlsx", "xls"])
        excel_file2 = st.sidebar.file_uploader("Charger un second fichier Excel si besoin (dates plus récentes)", type=["xlsx", "xls"])

        if excel_file is not None and excel_file2 is not None:
            # Charger le fichier Excel dans un DataFrame pandas
            df1 = pd.read_excel(excel_file, header=None)
            df2 = pd.read_excel(excel_file2, header=None)
            df=pd.concat([df1,df2])
        elif excel_file is None and excel_file2 is not None:
            # Charger le fichier Excel dans un DataFrame pandas
            df = pd.read_excel(excel_file2, header=None)
        elif excel_file is not None and excel_file2 is None:
            df = pd.read_excel(excel_file, header=None)  
        else:
            st.write("Maintenant vous allez pouvoir charger votre fichier excel pour commencer.")  

        if excel_file or excel_file2 is not None:   
            if len(df.columns)==11:
                colonnes = ['Date', 'Titre', 'Nom', 'Prénom', 'mail', 'Site', 'Type', 'Date_début', 'Date_fin', 'col', 'Formation']
                df.columns = colonnes
                df=df.drop(["Titre", "mail", "Type", "col", "Formation"], axis=1)
                df['Nom_Prénom']=df['Nom']+" "+df['Prénom']
                df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
                df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
                df['Date'] = df['Date'].fillna(method='ffill')
                df['Durée'] = df.apply(calculate_duration, axis=1)
            else:
                colonnes = ['Date', 'Titre', 'Nom', 'Prénom', 'mail', 'Site', 'Type', 'Date_début', 'Date_fin']
                df.columns = colonnes
                df=df.drop(["Titre", "mail", "Type"], axis=1)
                df['Nom_Prénom']=df['Nom']+" "+df['Prénom']
                df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
                df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
                df['Date'] = df['Date'].fillna(method='ffill')
                df['Durée'] = df.apply(calculate_duration, axis=1)

        if page == pages[1]:
            st.title("RH ART")
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
                couleurs_sites = {"St etienne": 'green', "Lyon": 'blue', "Bordeaux":'red', "Rennes":'yellow', 
                                "Marseille": 'lightblue', "Dijon":'orange', "Clermont":"purple", "Brest":'grey'}
                grouped_data = df_filtre.groupby(['Nom_Prénom', 'Site'])['Durée'].sum().reset_index()
                fig1=plt.figure(figsize=(20, 12))
                sns.barplot(x='Nom_Prénom', y='Durée', hue='Site', data=grouped_data, palette=couleurs_sites)
                plt.title(f"Durée totale réalisée par ART pour le mois de {mois_select}.")
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

            else:
                st.write(f"Aucune donnée disponible pour le mois {mois_select}.")
        
        
    else:
        st.error("Mot de passe incorrect")
 
if __name__ == '__main__':
    main()

    