//to fetch the movies on which user clicked
function movie_clicked(id){
	console.log("movie id clicked:", id);
	fetch('/store_liked_movie', {
    	method: 'POST',
    	body: new URLSearchParams({ clicked_id: id })
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.error(error));
}

//to implement show more functionality
currentPage=1
hasMoreData=true;
function load_more_data(){
	$('#loading-spinner').show();
	$('#show-more-button').hide();
	
	$.ajax({
		url: '/get-more-data',
    	type: 'GET',
    	data: {page: currentPage},
    	success: function(response){
    		newMovies = response.data;
    		for (var i = 0; i < newMovies.length; i++) {
        		var movie_data = newMovies[i];
        		var movieTemplate = `<a class="movie" onclick="movie_clicked('${movie_data.id}')">
						<img src="static/${movie_data.thumbnail_location}">
						${movie_data.title} (${movie_data.release_year})
					</a>
            	`;
            	$('#movies-container').append(movieTemplate);
            }
			currentPage++;
      
			hasMoreData = response.has_more;
			if (hasMoreData){
				$('#show-more-button').show();
			}
      
			$('#loading-spinner').hide();
    	},
    	error: function(error){
    		console.error("Error:", error);
    	}
    });
}

//to shorten movie title
function shortenTitle(title, maxlength=40){
	if(title.length > maxlength){
		return title.substring(0, maxlength) + "...";
	} else {
		return title;
	}
}