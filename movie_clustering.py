import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pickle

#pd.set_option("display.max_rows", None)
movie_data=pd.read_csv("datasets/processed_data.csv")

xdata=movie_data.drop(["id", "title", "list_genres", "keywords", "original_language", "scaled_year", "popularity", "list_companies"], axis=1)
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

model=KMeans(n_clusters=67, n_init='auto')

pca=PCA(0.95)
x_pca=pca.fit_transform(xdata)
movie_data['clusters']=model.fit_predict(x_pca)

centroid=model.cluster_centers_
#print("cluster centroids:", centroid)

#Performance metrics in clustering
score=silhouette_score(x_pca, movie_data.clusters)
print("score:", score)

#Saving clustered model
with open("models/kmeans_model.pickle", 'wb') as file:
	pickle.dump(model, file)
	
#Saving pca model
with open("models/pca_model.pickle", 'wb') as file:
	pickle.dump(pca, file)

#saving processed data
processed_data=movie_data.rename(columns={'genres': 'list_genres', 'production_companies': 'list_companies'})
processed_data.to_csv("datasets/processed_data.csv", index=False)

def get_input_data(genres, lang, year, companies, vote_avg):
	cols=list(xdata.columns)
	data=np.zeros(len(cols))
	
	for genre in genres:
		if "genre_"+genre in cols:
			data[cols.index("genre_"+genre)]=1
	
	for company in companies:
		if "company_"+company in cols:
			data[cols.index("company_"+company)]=1
	
	if "lang_"+lang in cols:
		data[cols.index("lang_"+lang)]=True
	
	data[cols.index("release_year")]=year
	#data[cols.index("popularity")]=popularity
	data[cols.index("vote_average")]=vote_avg
	return pca.transform(data.reshape(1,-1))

def recommend_movies(genre=[], lang='en', year=2010, company=[], vote_avg=1, num=10):
	data=get_input_data(genre, lang, year, company, vote_avg)
	cluster=model.predict(data)[0]
	cluster_movies=movie_data[movie_data.clusters==cluster]
	recommended=cluster_movies.sort_values(by="popularity", ascending=False)
	recommended=recommended.head(num)[['id', 'title', 'release_year']]
	recommended.index=range(0, num)
	return recommended

if __name__=="__main__":
	recommendations=recommend_movies()
	print(recommendations)