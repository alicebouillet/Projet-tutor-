import pandas as pd

def lecture_donnees():
    data_calendrier = pd.read_csv("data/calendar.csv.gz", sep=",")
    data_listings = pd.read_csv("data/listings.csv.gz", sep=",")
    data_reviews = pd.read_csv("data/reviews.csv.gz", sep=",")
    data_neighbourhoods = pd.read_csv("data/neighbourhoods.csv", sep=",")
    return data_calendrier, data_listings, data_reviews, data_neighbourhoods

data_calendrier, data_listings, data_reviews, data_neighbourhoods = lecture_donnees()
