from flask import Flask, render_template, request, url_for, jsonify
from knn_recommendations import movie_recommendations, show_metrics
from preferences import store_preferences, analyse_preferences
from search_movies import search_by_title, filter_by_features
import pandas as pd
import numpy as np
import json

app=Flask(__name__)

with open("datasets/available_options.json", 'r') as file:
	available_options=json.loads(file.read())

#movies_per_page
per_page=20

search_input=''

@app.route('/store_liked_movie', methods=['GET', 'POST'])
def store_liked_movie():
	if request.method=='POST':
		liked_id=int(request.form['clicked_id'])
		store_preferences(liked_id, liked_data)
		return "recieved succesfully!"
	else:
		return "Invalid request!"

@app.route('/get-more-data', methods=['GET', 'POST'])
def get_more_data():
	page=int(request.args['page'])
	
	global filtered
	if not filtered:
		more_movies=movies.iloc[page*per_page: (page+1)*per_page, :]
	else:
		more_movies=filtered_movies.iloc[page*per_page: (page+1)*per_page, :]
	
	if per_page>len(more_movies):
		more=False
	else:
		more=True
	
	return {
		'data': more_movies.to_dict(orient="records"),
		'has_more': more
	}

@app.route('/get_metrics')
def get_metrics():
	metrics=show_metrics()
	data={"metrics": metrics}
	return jsonify(data)

@app.route('/filter-movies', methods=['GET', 'POST'])
def filter_movies():
	filter=request.args.to_dict()
	genre=filter['select_genres']
	lang=filter['select_language']
	year=filter['select_year']
	
	global filtered_movies, search_input
	if search_input:
		filtered_movies=filter_by_features(genre, lang, year, movies)
	else:
		filtered_movies=filter_by_features(genre, lang, year)
	
	global filtered
	filtered=True
	return jsonify(data=filtered_movies.to_dict(orient="records")[:per_page])

@app.route('/', methods=['GET', 'POST'])
def homepage():
	global movies, filtered, search_input
	filtered=False
	if request.method=='POST':
		search_input=request.form['search-input']
		movies=search_by_title(search_input, 50)
		return render_template("movie.html", search_input=search_input, options=available_options, movies=movies.to_dict(orient="records")[:per_page])
	else:
		search_input=''
		preference=analyse_preferences()
		movies=movie_recommendations(preference)
		
		global liked_data
		liked_data=pd.DataFrame({
			"id": movies.id,
			"liked": np.zeros(len(movies))
		})
		
		return render_template("movie.html", options=available_options, movies=movies.to_dict(orient="records")[:per_page])

if __name__=="__main__":
	app.run(debug=True)