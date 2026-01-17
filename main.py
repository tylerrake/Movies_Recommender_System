import streamlit as st
import pickle
import pandas as pd
import requests
import urllib.parse

st.set_page_config(
    page_title="Movie Recommender System",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
.stApp {
    background-color: black;
}

h1, h2, h3, h4, h5, p, span, label {
    color: white !important;
}

.stSelectbox > div > div {
    background-color: #1a1a1a;
    color: white;
}

/* Normal buttons */
div.stButton > button {
    background-color: #e50914;
    color: white;
    border-radius: 6px;
    padding: 0.6em 2em;
    font-size: 16px;
    font-weight: bold;
    border: none;
}

/* RED link_button styling */
a[data-testid="stLinkButton"] {
    background-color: #e50914 !important;
    color: white !important;
    padding: 0.6em 1.8em;
    border-radius: 6px;
    font-weight: bold;
    text-decoration: none !important;
    display: inline-block;
    text-align: center;
}

a[data-testid="stLinkButton"]:hover {
    background-color: #b20710 !important;
    color: white !important;
}

img {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

similarity_story = pickle.load(open("similarity_story.pkl", "rb"))
similarity_genre = pickle.load(open("similarity_genre.pkl", "rb"))


@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        url = (
            f"https://api.themoviedb.org/3/movie/{movie_id}"
            f"?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        )
        data = requests.get(url, timeout=5).json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except:
        pass

    return "https://placehold.co/500x750/000000/FFFFFF?text=No+Poster"


def youtube_trailer_link(movie_title):
    query = urllib.parse.quote(movie_title + " official trailer")
    return f"https://www.youtube.com/results?search_query={query}"


# RECOMMENDATION FUNCTION

def recommend(movie, mode):
    index = movies[movies['title'] == movie].index[0]

    similarity_matrix = (
        similarity_story if mode == "Storytelling-based"
        else similarity_genre
    )

    distances = sorted(
        list(enumerate(similarity_matrix[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    results = []
    for movie_idx, score in distances[1:6]:
        movie_id = movies.iloc[movie_idx].movie_id
        results.append({
            "title": movies.iloc[movie_idx].title,
            "poster": fetch_poster(movie_id),
            "score": round(score * 100, 2)
        })

    return results


# HEADER

st.markdown(
    "<h1 style='text-align:center;'> Movie Recommendation System</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>"
    "Storytelling & Genre-Based AI Movie Recommender"
    "</p>",
    unsafe_allow_html=True
)

st.markdown("---")


# MOVIE SELECTION

selected_movie = st.selectbox(
    "Select a movie you like",
    movies['title'].values
)


mode = st.radio(
    "Recommendation Mode",
    ["Storytelling-based", "Genre-based"],
    horizontal=True
)

if mode == "Storytelling-based":
    st.caption(" Recommendations based on plot, themes, and narrative similarity")
else:
    st.caption(" Recommendations based on genre similarity")


st.subheader(" Selected Movie")

selected_movie_id = movies[movies['title'] == selected_movie].movie_id.values[0]
st.image(fetch_poster(selected_movie_id), width=260)


if st.button("Recommend"):
    with st.spinner("Finding similar movies and loading posters..."):
        recommendations = recommend(selected_movie, mode)

    st.markdown("##  Recommended Movies")

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.markdown(f"**{recommendations[idx]['title']}**")
            st.image(recommendations[idx]['poster'], use_container_width=True)

            trailer_url = youtube_trailer_link(recommendations[idx]['title'])
            st.markdown(
               f"""
               <a href="{trailer_url}" target="_blank"
                 style="
                      display: inline-block;
                      background-color: #e50914;
                      color: white;
                      padding: 10px 18px;
                      border-radius: 6px;
                      text-decoration: none;
                      font-weight: bold;
                      text-align: center;
                      margin-top: 8px;
                ">
                Watch Trailer on YouTube
              </a>
              """,
             unsafe_allow_html=True
)



