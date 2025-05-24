from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests

app = Flask(__name__)

# Load data
movies = pd.DataFrame(pickle.load(open('movie_dict.pkl', 'rb')))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c144e3bf9993a2b5c0cef94118487d04"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except:
        pass
    return "https://via.placeholder.com/300x450?text=Poster+Not+Available"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
    return recommended_movie_names, recommended_movie_posters

@app.route('/', methods=['GET', 'POST'])
def home():
    movie_list = movies['title'].values
    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        names, posters = recommend(selected_movie)
        
        return render_template('recommend.html', movie_data=zip(names, posters))

    return render_template('index.html', movie_list=movie_list)

if __name__ == '__main__':
    app.run(debug=True)
