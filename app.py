from flask import Flask, render_template, request, url_for
from recommendations import movie_recommendations, store_preferences

app=Flask(__name__)

#movies_per_page
per_page=20

@app.route('/store_liked_movie', methods=['GET', 'POST'])
def store_liked_movie():
	if request.method=='POST':
		liked_id=int(request.form['clicked_id'])
		store_preferences(liked_id)
		return "recieved succesfully!"
	else:
		return "Invalid request!"

@app.route('/get-more-data', methods=['GET', 'POST'])
def get_more_data():
	page=int(request.args['page'])
	more_movies=movies[page*per_page: (page+1)*per_page]
	if per_page>len(more_movies):
		more=False
	else:
		more=True
	
	return {
		'data': more_movies,
		'has_more': more
	}

@app.route('/', methods=['GET', 'POST'])
def homepage():
	global movies
	if request.method=='POST':
		search_input=request.form['search-input']
		movies=movie_recommendations(search_input).to_dict(orient="records")
		return render_template("movie.html", search_input=search_input, movies=movies[:per_page])
	else:
		movies=movie_recommendations('').to_dict(orient="records")
		return render_template("movie.html", movies=movies[:per_page])

if __name__=="__main__":
	app.run(debug=True)