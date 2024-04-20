import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pickle
#pd.set_option('display.max_columns', None)

#reading dataset
movies=pd.read_csv("tmdb_5000_movies.csv")

#choosing only important features
data=movies[['id', 'genres', 'original_language', 'popularity', 'release_date', 'vote_average', 'title']]

#checking and removing null values
print(data.isna().sum())
data.dropna(inplace=True)
#print(data.nunique())

#preprocessing genres
def convert_to_text(data):
	processed=[]
	for dic in eval(data):
		processed.append(dic['name'].lower().strip())
	if len(processed)==0:
		processed.append('none')
	return processed

data['genres']=data['genres'].apply(convert_to_text)
#print(data)

data['release_year']=data['release_date'].apply(lambda date: int(date.split('-')[0]))

scaler=MinMaxScaler()
data['popularity']=scaler.fit_transform(data[['popularity']])
data['vote_average']=scaler.fit_transform(data[['vote_average']])

#preprocessing languages
lang_values=data.original_language.value_counts()
rare_lang=lang_values[lang_values<=5].index
print(rare_lang)
data.loc[data.original_language.isin(rare_lang), "original_language"]="other"

#text extraction by encoding text data
genre_dummies=pd.get_dummies(data.genres.apply(pd.Series).stack(), prefix="genre").groupby(level=0).sum().drop("genre_none", axis=1)
#print(genre_dummies)
language_dummies=pd.get_dummies(data.original_language, prefix="lang", dtype=int).drop("lang_other", axis=1)
#print(language_dummies)

movie_data=pd.concat([genre_dummies, language_dummies, data.drop(["genres", "original_language", "release_date"], axis=1)], axis=1)
xdata=movie_data.drop(["id", "title"], axis=1)
print(xdata.columns)

#Elbow Method for finding no. of clusters
rng=[i for i in range(1,100)]
sse=[]
#for k in rng:
	#kmeans=KMeans(n_clusters=k, n_init='auto')
	#kmeans.fit(xdata)
	#sse.append(kmeans.inertia_)

#plt.plot(rng, sse)
#plt.show()

model=KMeans(n_clusters=10, n_init='auto')
movie_data['clusters']=model.fit_predict(xdata)

centroid=model.cluster_centers_
#print("cluster centroids:", centroid)

#Performance metrics in clustering
score=silhouette_score(xdata, movie_data.clusters)
print("score:", score)

#Saving clustered model
with open("model.pickle", 'wb') as file:
	pickle.dump(model, file)
	
#saving processed data
movie_data.to_csv("processed_data.csv", index=False)

def get_input_data(genres, lang, year, popularity, vote_average):
	cols=list(xdata.columns)
	data=np.zeros(len(cols))
	
	for genre in genres:
		if "genre_"+genre in cols:
			data[cols.index("genre_"+genre)]=1
	
	if "lang_"+lang in cols:
		data[cols.index("lang_"+lang)]=True
	
	data[cols.index("release_year")]=year
	data[cols.index("popularity")]=popularity
	data[cols.index("vote_average")]=vote_average
	return data.reshape(1,-1)

def recommend_movies(genre=[], lang='en', year=2010, popularity=10, vote_average=5, num=10):
	data=get_input_data(genre, lang, year, popularity, vote_average)
	cluster=model.predict(data)[0]
	cluster_movies=movie_data[movie_data.clusters==cluster]
	recommended=cluster_movies.sort_values(by="popularity", ascending=False)
	recommended=recommended.head(num)[['id', 'title', 'release_year']]
	recommended.index=range(0, num)
	return recommended

if __name__=="__main__":
	recommendations=recommend_movies()
	print(recommendations)