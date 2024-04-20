import requests
import pandas as pd
import threading

# TMDb API key
api_key="1d36b09ad72e809c27a05b7a9649c11f"

movies_data = pd.read_csv("tmdb_5000_movies.csv")

def get_thumbnails(movie_id, lang):
	# Construct URL for TMDb API request
	url = f'https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={api_key}'

	# Make request to TMDb API
	response = requests.get(url)
	data = response.json()

	image_data = [image for image in data['posters'] if image['aspect_ratio']>0.65 and image['iso_639_1']==lang]
	if not image_data:
		print("No such image found")
		
	# Get the URL of the thumbnail image (assuming the first image in the list)
	image_url = f"https://image.tmdb.org/t/p/w500{image_data[0]['file_path']}"

	# Download the image
	img = requests.get(image_url).content
	with open(f'static/thumbnails/{movie_id}.jpg', 'wb') as f:
	   f.write(img)
	print(movie_id, "Image successfully downloaded")
    
threads = []
for index, movie in movies_data[['id', 'original_language']].iterrows():
	thread = threading.Thread(target=get_thumbnails, args=(movie.id, movie.original_language))
	threads.append(thread)
	thread.start()

for thread in threads:
	thread.join()

processed_data = pd.read_csv("processed_data.csv")
processed_data['thumbnail_location'] = processed_data['id'].apply(lambda id: f"thumbnails/{id}.jpg")
processed_data.to_csv("processed_data.csv", index=False)
print("Thumbnail locations saved successfully")