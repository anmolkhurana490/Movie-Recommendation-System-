import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from iso639 import Lang
import pickle

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

stopwords=stopwords.words('english')
#print(stopwords)

import string
puncts=list(string.punctuation)
print(puncts)

#pd.set_option('display.max_columns', None)

#reading dataset
movies=pd.read_csv("datasets/tmdb_5000_movies.csv")

#choosing only important features
data=movies[['id', 'genres', 'original_language', 'release_date', 'keywords', 'production_companies', 'popularity', 'vote_average', 'title']]

#checking and removing null values
print(data.isna().sum())
data.dropna(inplace=True)
#print(data.nunique())

#preprocessing genres
def convert_to_text(data):
    processed=[]
    for dic in eval(data):
        name=dic['name'].lower().strip()
        processed.append(name)
    if len(processed)==0:
        processed.append('none')
    return processed

data['genres']=data['genres'].apply(convert_to_text)
#print(data)
data['production_companies']=data['production_companies'].apply(convert_to_text)
#print(data)

def process_keywords(keywords):
    processed=[]
    for punc in puncts:
        if punc in keywords:
            keywords=keywords.replace(punc, '')
    words=keywords.split()
    for word in words:
        if not word in stopwords:
            processed.append(word)
    unique_words=pd.Series(processed).unique()
    return list(unique_words)

data["keywords"]=data["keywords"].apply(convert_to_text)
data["keywords"]=data["keywords"].apply(lambda value: process_keywords(' '.join(value)))
print(data["keywords"])

data['release_year']=data['release_date'].apply(lambda date: int(date.split('-')[0]))
data=data.loc[data['release_year']>1950] #release year outlier removal

year_scaler=MinMaxScaler()
data['scaled_year']=year_scaler.fit_transform(data[['release_year']])

#Saving year_scaler model
with open("models/year_scaler.pickle", 'wb') as file:
	pickle.dump(year_scaler, file)

vote_scaler=MinMaxScaler()
#data['popularity']=scaler.fit_transform(data[['popularity']])
data['vote_average']=vote_scaler.fit_transform(data[['vote_average']])

#preprocessing languages
data.loc[data["original_language"]=="cn", "original_language"]="zh"
lang_values=data.original_language.value_counts()
rare_lang=lang_values[lang_values<=5].index
print(rare_lang)
data.loc[data.original_language.isin(rare_lang), "original_language"]="other"

data["original_language"]=data["original_language"].apply(lambda lang_code: Lang(lang_code).name if lang_code!="other" else "other")

#like top companies, top keywords
def get_top_values(data_col):
	series=pd.Series()
	#companies, keywords for each movie
	for value in data_col:
		series=series._append(pd.Series(value))
	
	unique_values=series.value_counts()
	top_values=unique_values[unique_values>=5]
	return top_values.index

def process_top_values_list(values, top_values):
	inter=list(set(values) & set(top_values))
	if len(inter):
		return inter
	else:
		return ["others"]

top_companies=get_top_values(data["production_companies"])
data["production_companies"]=data["production_companies"].apply(lambda value: process_top_values_list(value, top_companies))

#text extraction by encoding text data
genre_dummies=pd.get_dummies(data.genres.apply(pd.Series).stack(), prefix="genre").groupby(level=0).sum().drop("genre_none", axis=1)
#print(genre_dummies)
language_dummies=pd.get_dummies(data.original_language, prefix="lang", dtype=int).drop("lang_other", axis=1)
#print(language_dummies)
company_dummies=pd.get_dummies(data.production_companies.apply(pd.Series).stack(), prefix="company").groupby(level=0).sum().drop("company_none", axis=1)
#print(company_dummies)

movie_data=pd.concat([data.drop(["release_date"], axis=1), genre_dummies, language_dummies, company_dummies], axis=1)

#saving processed data
processed_data=movie_data.rename(columns={'genres': 'list_genres', 'production_companies': 'list_companies'})
processed_data.to_csv("datasets/processed_data.csv", index=False)
print("Processed Data Saved Successfully")