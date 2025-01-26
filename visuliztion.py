import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np

ratings_file = 'ratings.dat'
movies_file = 'movies.dat'
users_file = 'users.dat'

def load_ratings(file):
    ratings = []
    with open(file, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            user_id, movie_id, rating, timestamp = line.strip().split("::")
            ratings.append((int(user_id), int(movie_id), float(rating)))
    return ratings

def load_movies(file):
    movies = {}
    with open(file, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            movie_id, title, genres = line.strip().split("::")
            movies[int(movie_id)] = {'title': title, 'genres': genres.split("|")}
    return movies

def load_users(file):
    users = {}
    with open(file, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            user_id, gender, age, occupation, _ = line.strip().split("::")
            users[int(user_id)] = {'gender': gender, 'age': int(age), 'occupation': int(occupation)}
    return users

ratings = load_ratings(ratings_file)
movies = load_movies(movies_file)
users = load_users(users_file)

st.sidebar.title("Movie Data Dashboard")
selected_visualization = st.sidebar.selectbox(
    "Select Visualization", 
    ["Distribution of Ratings by Genres and Years", "Popular Genres by User Demographics", "Heatmap of Genre Correlation"]
)

if selected_visualization == "Distribution of Ratings by Genres and Years":
    st.title("Distribution of Ratings by Genres and Years")

    genre_ratings = defaultdict(list)
    year_ratings = defaultdict(list)

    for user_id, movie_id, rating in ratings:
        if movie_id in movies:
            movie = movies[movie_id]
            genres = movie['genres']
            for genre in genres:
                genre_ratings[genre].append(rating)

          
            if '(' in movie['title'] and ')' in movie['title']:
                year = movie['title'].split('(')[-1].replace(')', '')
                if year.isdigit():
                    year_ratings[int(year)].append(rating)

    
    avg_genre_ratings = {genre: np.mean(ratings) for genre, ratings in genre_ratings.items()}
    genres, avg_ratings = zip(*sorted(avg_genre_ratings.items(), key=lambda x: x[1], reverse=True))

    plt.figure(figsize=(10, 6))
    plt.barh(genres, avg_ratings, color='skyblue')
    plt.xlabel("Average Rating")
    plt.ylabel("Genre")
    plt.title("Average Ratings by Genre")
    st.pyplot(plt)

    avg_year_ratings = {year: np.mean(ratings) for year, ratings in year_ratings.items()}
    years, avg_ratings = zip(*sorted(avg_year_ratings.items()))

    plt.figure(figsize=(10, 6))
    plt.plot(years, avg_ratings, marker='o', color='green')
    plt.xlabel("Year")
    plt.ylabel("Average Rating")
    plt.title("Average Ratings by Year")
    st.pyplot(plt)

elif selected_visualization == "Popular Genres by User Demographics":
    st.title("Popular Genres by User Demographics")

    gender_genre_ratings = {'M': defaultdict(list), 'F': defaultdict(list)}
    for user_id, movie_id, rating in ratings:
        if user_id in users and movie_id in movies:
            gender = users[user_id]['gender']
            genres = movies[movie_id]['genres']
            for genre in genres:
                gender_genre_ratings[gender][genre].append(rating)

    avg_gender_genre_ratings = {
        gender: {genre: np.mean(ratings) for genre, ratings in genre_ratings.items()}
        for gender, genre_ratings in gender_genre_ratings.items()
    }

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax, (gender, ratings) in zip(axes, avg_gender_genre_ratings.items()):
        genres, avg_ratings = zip(*sorted(ratings.items(), key=lambda x: x[1], reverse=True))
        ax.barh(genres, avg_ratings, color='orange' if gender == 'M' else 'purple')
        ax.set_title(f"Average Ratings by Genre ({gender})")
        ax.set_xlabel("Average Rating")

    st.pyplot(fig)

elif selected_visualization == "Heatmap of Genre Correlation":
    st.title("Heatmap of Genre Correlation")

    genre_ratings = defaultdict(list)
    for _, movie_id, rating in ratings:
        if movie_id in movies:
            genres = movies[movie_id]['genres']
            for genre in genres:
                genre_ratings[genre].append(rating)

    genres = list(genre_ratings.keys())
    matrix = np.zeros((len(genres), len(genres)))

    for i, genre1 in enumerate(genres):
        for j, genre2 in enumerate(genres):
            if i <= j:
                common_ratings = min(len(genre_ratings[genre1]), len(genre_ratings[genre2]))
                correlation = np.corrcoef(
                    genre_ratings[genre1][:common_ratings], genre_ratings[genre2][:common_ratings]
                )[0, 1] if common_ratings > 1 else 0
                matrix[i][j] = matrix[j][i] = correlation

    plt.figure(figsize=(12, 8))
    sns.heatmap(matrix, xticklabels=genres, yticklabels=genres, annot=False, cmap="coolwarm")
    plt.title("Correlation Between Genres")
    st.pyplot(plt)
