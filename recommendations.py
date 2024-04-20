import numpy as np
import pandas as pd
import pickle
#pd.set_option("display.max_columns", None)
movie_data=pd.read_csv("processed_data.csv")
cols=list(movie_data.drop(["id", "title", "thumbnail_location"], axis=1).columns)


#to store available options in genres, language, etc.
available_options={
	"genres": [],
	"lang": []
}

for col in cols:
	if col.startswith("genre"):
		available_options["genres"].append(col.split('_')[1])
	if col.startswith("lang"):
		available_options["lang"].append(col.split('_')[1])

#print(available_options)

def load_model():
	with open("model.pickle", "rb") as file:
		return pickle.load(file)

def get_input_data(genres, langs, year, popularity, vote_average):
	data=np.zeros(len(cols)-1) #clusters column not required
	
	for genre in genres:
		if genre in available_options["genres"]:
			data[cols.index("genre_"+genre)]=1
	
	for lang in langs:
		if lang in available_options["lang"]:
			data[cols.index("lang_"+lang)]=1
	
	data[cols.index("release_year")]=year
	data[cols.index("popularity")]=popularity
	data[cols.index("vote_average")]=vote_average
	return data.reshape(1,-1)

def recommend_movies(genre, lang, year, popularity, vote_average, num):
	model=load_model()
	data=get_input_data(genre, lang, year, popularity, vote_average)
	cluster=model.predict(data)[0]
	cluster_movies=movie_data[movie_data.clusters==cluster]
	recommended=cluster_movies.sort_values(by="popularity", ascending=False)
	recommended=recommended.head(num)[['id', 'title', 'release_year', 'thumbnail_location']]
	recommended.index=range(0, num)
	return recommended

def display_recommendations(preference, searched, num):
	#Display Movie Recommendations
	#print("Movie Recommendations:")
	
	#Merging data in searched and preference
	genres=preference["genres"]
	langs=preference["langs"]
	year=preference["release_year"]
	popularity=preference["popularity"]
	vote_average=preference["vote_average"]
	
	if searched:
		if searched['genre']:
			genres=searched['genre']
			
		if searched['lang']:
			langs=[searched['lang']]
			
		if searched['year']:
			year=searched['year']
	
	recommendations=recommend_movies(genre=genres, lang=langs, year=year, popularity=popularity, vote_average=vote_average, num=num)
	return recommendations

#Collecting Liked data and Storing User Preferences in CSV file
def store_preferences(movie_id):
	#print("Which Movies do you like?")
	#liked=list(map(int, input("Enter their index: ").split()))
	liked_movie=movie_data.loc[movie_data.id==movie_id].iloc[0]
	genres=[]
	for col in cols:
		if col.startswith("genre") and liked_movie[col]:
			genres.append(col.split('_')[1])
	
	lang=[]
	for col in cols:
		if col.startswith("lang") and liked_movie[col]:
			lang.append(col.split('_')[1])
	
	row=f"{'|'.join(genres)},{'|'.join(lang)},{liked_movie['release_year']},{liked_movie['popularity']},{liked_movie['vote_average']}"
	print(row)
	with open("preferences.csv", "a") as file:
		file.write("\n"+row)
	
	print("Your preference collected")

#used to create new preference data in csv
def new_preferences():
	with open("preferences.csv", "w") as file:
		file.write("genre,language,release_year,popularity,vote_average")


def analyse_preferences():
	preferences=pd.read_csv("preferences.csv")
	#if no preferences stored
	if preferences.size==0:
		return {
			"genres": [],
			"langs": [],
			"release_year": 2010,
			"popularity": 1,
			"vote_average": 1
		}
	
	#using index to give more weight to newer preferences
	index=preferences.index+1
	#for text data, will take frequent text
	#for numerical values, will take average
	genre_series=pd.Series((preferences.genre+'|').dot(index).split('|')[:-1])
	preferred_genres=genre_series.value_counts()[:4].index
	
	lang_series=pd.Series((preferences.language+'|').dot(index).split('|')[:-1])
	preferred_langs=lang_series.value_counts()[:4].index
		
	release_year=preferences.release_year.dot(index)//sum(index)
	popularity=preferences.popularity.dot(index)/sum(index)
	vote_average=preferences.vote_average.dot(index)/sum(index)
	
	return {
		"genres": list(preferred_genres),
		"langs": list(preferred_langs),
		"release_year": release_year, 
		"popularity": popularity, 
		"vote_average": vote_average
	}

#Intakes and analyses search input
def analyse_search_input(search_query):
	search_list=search_query.split()
	genre=[]
	lang=None
	year=None
	
	for word in search_list:
		if word in available_options['genres']:
			genre.append(word)
		elif word in available_options['lang']:
			lang=word
		elif word.isdigit():
			num=int(word)
			if num>1900 and num<2050:
				year=num
	
	if search_query:			
		return {
			"genre": genre,
			"lang": lang,
			"year": year
		}

def movie_recommendations(search_input):
	searched=analyse_search_input(search_input)
	final_preference=analyse_preferences()
	print(final_preference)
	
	recommended_movies=display_recommendations(final_preference, searched, 200)
	return recommended_movies

if __name__=="__main__":
	new_preferences()
	
	#can search for genres, languages, year, etc.
	#like comedy en 2005
	search_input=input("Search: ")
	output=movie_recommendations(search_input)[:20]
	print(output)
