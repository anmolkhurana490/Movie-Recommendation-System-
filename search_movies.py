import pandas as pd
from fuzzywuzzy import fuzz
import json
import re

#pd.set_option("display.max_columns", None)
movie_data=pd.read_csv("datasets/processed_data.csv")

with open("datasets/available_options.json", "r") as file:
	available_options=json.loads(file.read())

#Intakes and analyses search input
def filter_by_features(genre, lang, year, movies=pd.DataFrame()):
	if movies.empty:
		filter_movies=movie_data
	else:
		filter_movies=movie_data.merge(movies[['id']], how='inner', on='id', sort=False)
	
	if genre!="all":
		movie_by_genre=filter_movies[filter_movies.list_genres.apply(lambda lst: genre in [item.split()[0] for item in eval(lst)])]
	else:
		movie_by_genre=filter_movies
	
	if lang!="all":
		movie_by_lang=filter_movies.loc[filter_movies.original_language==lang]
	else:
		movie_by_lang=filter_movies
	
	if year!="all":
		lower=int(year)
		movie_by_year=filter_movies[(filter_movies.release_year>=lower) & (filter_movies.release_year<=lower+5)]
	else:
		movie_by_year=filter_movies
	
	to_merge=[movie_by_lang, movie_by_year]
	results=movie_by_genre
	
	for movie_by_feature in to_merge:
		results=results.merge(movie_by_feature, how="inner", on="id")
	
	if movies.empty:
		results.sort_values(by="popularity", ascending=False, inplace=True)
	
	return results[["id", "title", "release_year", "thumbnail_location"]]
	
def search_by_title(search_text, num):
	search_query=re.sub(r'[^\w\s]', ' ', search_text) #punctuations removed
	movie_data["title_score"]=movie_data['title'].apply(lambda title: fuzz.partial_ratio(search_query.lower(), title.lower()))
	
	search_list=search_query.lower().split()
	movie_data["keyword_score"]=movie_data["keywords"].apply(lambda lst: len(set(eval(lst)) & set(search_list))/len(search_list)*100)
	movie_data["final_score"]=movie_data.apply(lambda row: (row["title_score"]*0.7)+(row["keyword_score"]*0.3), axis=1)
	
	if search_query.strip():
		results=movie_data.sort_values(by="final_score", ascending=False)[(movie_data.title_score>=75) | (movie_data.keyword_score>0)]
		return results[["id", "title", "release_year", "thumbnail_location"]][:num]
	else:
		return movie_data[["id", "title", "release_year", "thumbnail_location"]][:num]

if __name__=="__main__":
	search=input("Search: ")
	print("Available genres:", available_options["genres"])
	genres=input("Select genres: ").split()
	print("Available languages:", available_options["languages"])
	language=input("Select langauge: ")
	year=input("Select Year: ")
	results=search_by_title(search, 50)
	print(results)