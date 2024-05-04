import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
import pickle
import json

#pd.set_option("display.max_rows", None)
movie_data=pd.read_csv("datasets/processed_data.csv")

cols=list(movie_data.drop(["id", "title", "list_genres", "keywords", "original_language", "scaled_year", "list_companies", "popularity", "thumbnail_location"], axis=1).columns)

#to store available options in genres, language, etc.
available_options={
	"genres": [],
	"languages": [],
	"release_year": []
}

for col in cols:
	if col.startswith("genre"):
		available_options["genres"].append(col.split('_')[1])
	if col.startswith("lang"):
		available_options["languages"].append(col.split('_')[1])

year_range=5
min_year=movie_data["release_year"].min()
max_year=movie_data["release_year"].max()
for year in range(min_year-(min_year%year_range), max_year, year_range):
	available_options["release_year"].append(f"{year} - {year+year_range}")

with open("datasets/available_options.json", "w") as file:
	json.dump(available_options, file)

def load_model(name):
	with open(f"models/{name}.pickle", "rb") as file:
		return pickle.load(file)

def get_input_data(genres, lang, year, companies, vote_avg):
	data=np.zeros(len(cols)-1) #cluster coulmn not required
	
	for genre in genres:
		if genre in available_options["genres"]:
			data[cols.index("genre_"+genre)]=1
	
	for company in companies:
		if "company_"+company in cols:
			data[cols.index("company_"+company)]=1
	
	if lang in available_options["languages"]:
		data[cols.index("lang_"+lang)]=1
	
	data[cols.index("release_year")]=year
	data[cols.index("vote_average")]=vote_avg
	
	pca=load_model("pca_model")
	return pca.transform(data.reshape(1,-1))

def recommend_movies(genre, lang, year, company, vote_avg):
	model=load_model("kmeans_model")
	data=get_input_data(genre, lang, year, company, vote_avg)
	cluster=model.predict(data)[0]
	cluster_movies=movie_data[movie_data.clusters==cluster]
	recommended=cluster_movies.sort_values(by="popularity", ascending=False)
	recommended.reset_index(drop=True, inplace=True)
	return recommended

def display_recommendations(preference):
	#Display Movie Recommendations
	
	#if preferences are blank
	if not preference:
		recommendations=movie_data.sort_values(by="popularity", ascending=False)
		
	else:
		genres=preference["genres"]
		lang=preference["lang"]
		year=preference["release_year"]
		companies=preference["companies"]
		vote_avg=preference["vote_average"]
		recommendations=recommend_movies(genres, lang, year, companies, vote_avg)
	
	return recommendations[['id', 'title', 'release_year', 'thumbnail_location']]

def performance_metrics():
	liked_data=pd.read_csv("datasets/liked_data.csv")
	precision_scores=[]
	for k in range(len(liked_data)):
		relevant_count=sum(liked_data.liked[:k+1])
		precision=relevant_count/(k+1)
		precision_scores.append(precision)
	
	if len(liked_data):
		#Mean Absolute Precision Score
		map=average_precision_score(liked_data.liked, precision_scores)
		with open("datasets/performance.csv", "a") as file:
			file.write(f"{map}\n")

def show_metrics():
	performance=pd.read_csv("datasets/performance.csv", names=["precision"])
	return performance["precision"].mean()

def movie_recommendations(final_preference):
	performance_metrics()
	recommended_movies=display_recommendations(final_preference)
	
	return recommended_movies


if __name__=="__main__":
	print(show_metrics())
	output=movie_recommendations({})
	print(output)
