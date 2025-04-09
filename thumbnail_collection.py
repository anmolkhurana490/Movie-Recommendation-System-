import requests
import pandas as pd
from iso639 import Lang
import threading
import time

# TMDb API key
api_key="1d36b09ad72e809c27a05b7a9649c11f"

movies_data = pd.read_csv("datasets/processed_data.csv")

def get_lang_code(lang):
	if lang!="other":
		try:
			return Lang(lang).pt1
		except:
			print(lang)
			return lang
	
movies_data["lang_code"] = movies_data["original_language"].apply(get_lang_code)

def get_thumbnails(movie_id, lang):
	# Construct URL for TMDb API request
	url = f'https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={api_key}'

	# Make request to TMDb APIll
	response = requests.get(url)
	data = response.json()
	image_data = [image for image in data['posters'] if image['aspect_ratio']>0.65 and image['iso_639_1']==lang]
	if not image_data:
		print("No such image found")
		print(image_data)
		
	else:
		# Get the URL of the thumbnail image (assuming the first image in the list)
		image_url = f"https://image.tmdb.org/t/p/w500{image_data[0]['file_path']}"

		# Download the image
		img = requests.get(image_url).content
		with open(f'static/thumbnails/{movie_id}.jpg', 'wb') as f:
			f.write(img)
		print(movie_id, "Image successfully downloaded")
    
threads = []
for index, movie in movies_data[['id', 'lang_code']].iterrows():
	thread = threading.Thread(target=get_thumbnails, args=(movie.id, movie.lang_code))
	threads.append(thread)
	thread.start()

for thread in threads:
	thread.join()

movies_data['thumbnail_location'] = movies_data['id'].apply(lambda id: f"thumbnails/{id}.jpg")
movies_data.drop("lang_code", axis=1, inplace=True)
movies_data.to_csv("datasets/processed_data.csv", index=False)
print("Thumbnail locations saved successfully")