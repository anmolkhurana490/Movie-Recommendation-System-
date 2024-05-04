import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import average_precision_score
import pickle

#pd.set_option("display.max_rows", None)
movie_data=pd.read_csv("datasets/processed_data.csv")

cols=list(movie_data.drop(["id", "title", "list_genres", "keywords", "original_language", "release_year", "list_companies", "popularity", "clusters", "thumbnail_location"], axis=1).columns)

#to store available options in genres, language, etc.
available_options={
	"genres": [],
	"languages": []
}

for col in cols:
	if col.startswith("genre"):
		available_options["genres"].append(col.split('_')[1])
	if col.startswith("languages"):
		available_options["languages"].append(col.split('_')[1])

#print(available_options)

def load_model(name):
	with open(f"models/{name}.pickle", "rb") as file:
		return pickle.load(file)

#Fitting our KNN model
xdata=movie_data[cols]
y=pd.Series([1]*xdata.shape[0])
knn=KNeighborsClassifier()
knn.fit(xdata, y)

def get_input_data(genres, lang, year, companies, vote_avg):
	data=np.zeros(len(cols))
	
	for genre in genres:
		if genre in available_options["genres"]:
			data[cols.index("genre_"+genre)]=1
	
	for company in companies:
		if "company_"+company in cols:
			data[cols.index("company_"+company)]=1
	
	if lang in available_options["languages"]:
		data[cols.index("lang_"+lang)]=1
	
	data[cols.index("scaled_year")]=load_model("year_scaler").transform([[year]])
	data[cols.index("vote_average")]=vote_avg
	
	return data.reshape(1,-1)

def recommend_movies(genre, lang, year, company, vote_average):
	data=get_input_data(genre, lang, year, company, vote_average)
	dist, ind=knn.kneighbors(data, n_neighbors=movie_data.shape[0], return_distance=True)
	recommended=movie_data.iloc[ind[0]]
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
	
	return recommendations[["id", "title", "release_year", "thumbnail_location"]]

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