import pandas as pd

movie_data=pd.read_csv("datasets/processed_data.csv")

#Collecting Liked data and Storing User Preferences in CSV file
def store_preferences(movie_id, liked_data):
	#print("Which Movies do you like?")
	preferences=pd.read_csv("datasets/preferences.csv")
	liked=movie_data.loc[movie_data.id==movie_id].iloc[0]
	row=[movie_id, liked.title, '|'.join(eval(liked.list_genres)), liked.original_language, liked.release_year, '|'.join(eval(liked.list_companies)), liked.vote_average]
	print(row)
	preferences.loc[len(preferences.index)]=row
	preferences.to_csv("datasets/preferences.csv", index=False)
	print("Your preference collected")
	
	#Collecting liked data for performace metrics
	liked_data.loc[liked_data.id==movie_id, "liked"]=1
	liked_data.to_csv("datasets/liked_data.csv", index=False)

#used to create new preference data in csv
def new_preferences():
	with open("datasets/preferences.csv", "w") as file:
		file.write("id,title,genre,language,release_year,company,vote_average")


def analyse_preferences():
	preferences=pd.read_csv("datasets/preferences.csv")
	#if no preferences stored
	if preferences.size==0:
		return {}
	
	#using index to give more weight to newer preferences
	index=preferences.index+1
	#for text data, will take frequent text
	#for numerical values, will take average
	genre_series=pd.Series((preferences.genre+'|').dot(index).split('|')[:-1])
	preferred_genres=genre_series.value_counts()[:4].index
	
	lang_series=pd.Series((preferences.language+'|').dot(index).split('|')[:-1])
	preferred_lang=lang_series.value_counts().index[0]
	
	company_series=pd.Series((preferences.company+'|').dot(index).split('|')[:-1])
	preferred_companies=company_series.value_counts()[:4].index
	
	release_year=preferences.release_year.dot(index)//sum(index)
	vote_avg=preferences.vote_average.dot(index)/sum(index)
	
	return {
		"genres": list(preferred_genres),
		"lang": preferred_lang,
		"release_year": release_year,
		"companies": list(preferred_companies),
		"vote_average": vote_avg
	}

if __name__=="__main__":
	preference=analyse_preferences()
	print(preference)
	new_preferences()