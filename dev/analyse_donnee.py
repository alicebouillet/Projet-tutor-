# Importation des bibliothèques nécessaires
import pandas as pd
from lecture_donnee import lecture_donnees

# Récupération des données
data_calendrier, data_listings, data_reviews, data_neighbourhoods = lecture_donnees()

#Début de l'analyse des données
print("Analyse des données du calendrier:")
print(data_calendrier.describe())

# Analyse valeurs manquantes
print(data_calendrier.isnull().sum())

print("Analyse des données des listings:")
print(data_listings.describe())
print(data_listings.isnull().sum())