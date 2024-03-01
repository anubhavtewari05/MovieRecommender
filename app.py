import streamlit as st
import pickle
import pandas as pd
import requests
import bz2file as bz2
import time

def decompress_pickle(file):
    model = bz2.BZ2File(file, 'rb')
    model = pickle.load(model)
    return model


def fetch_poster(movie_id):
    retries = 3
    delay = 3  # Delay in seconds before retrying

    for _ in range(retries):
        try:
            response = requests.get(
                'https://api.themoviedb.org/3/movie/{}?api_key=8fe5ff2c3388fae54605fe610fb5c1f8'.format(movie_id))
            if response.status_code == 200:
                data = response.json()
                poster_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
                return poster_url
            else:
                time.sleep(delay)
        except requests.ConnectionError as e:
            time.sleep(delay)

    return None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)
        if poster is not None:  # Check if poster is not None
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(poster)

    return recommended_movies, recommended_movies_posters

movies_list = pickle.load(open('movies_dict.pkl','rb'))
movies = pd.DataFrame(movies_list)
similarity = decompress_pickle('similarity.pbz2')

st.title('Movie Recommender System')
option_selected  = st.selectbox('Which movie do you like?',(movies['title'].values))
if st.button('Recommend'):
    names,posters = recommend(option_selected)

    col1, col2, col3, col4, col5 = st.columns(5)
    if names:
        with col1:
            st.text(names[0])  # Check if names list is not empty before accessing its elements
            st.image(posters[0])
        if len(names) > 1:
            with col2:
                st.text(names[1])
                st.image(posters[1])
        if len(names) > 2:
            with col3:
                st.text(names[2])
                st.image(posters[2])
        if len(names) > 3:
            with col4:
                st.text(names[3])
                st.image(posters[3])
        if len(names) > 4:
            with col5:
                st.text(names[4])
                st.image(posters[4])
    else:
        st.error("No recommendations found for this movie.")
