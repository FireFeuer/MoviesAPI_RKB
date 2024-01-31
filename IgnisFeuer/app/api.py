from flask import Flask, jsonify, request
from flask_restful import Api
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)
api = Api(app)

MOVIES = pd.DataFrame()
RATING = pd.DataFrame()
MOVIES_RATING = pd.DataFrame()

quantile = 0.9
count_points = 198


def loading():
    global MOVIES, RATING
    MOVIES = pd.read_csv(r"../Data_API/movies.csv")
    RATING = pd.read_csv(r"../Data_API/rating.csv")
    print("loading")

def update_movies_rating():
    global MOVIES_RATING

    MOVIES_RATING = RATING.merge(MOVIES, on='movieId')
    MOVIES_RATING.drop(columns="timestamp", inplace=True)
    MOVIES_RATING.drop(columns="genres", inplace=True)
    print("update_movies_rating")

def update_top10():

    global MOVIES_RATING, MOVIES

    avg_ratings = MOVIES_RATING.groupby('title')["rating"].mean().reset_index().rename(columns={'rating': 'avg_rating'})
    cnt_ratings = MOVIES_RATING.groupby('title')['rating'].count().reset_index().rename(columns={'rating': 'count_rating'})

    popular = avg_ratings.merge(cnt_ratings, on='title')

    v = popular["count_rating"]
    R = popular["avg_rating"]
    m = v.quantile(quantile)
    c = R.mean()
    popular['w_score'] = ((v * R) + (m * c)) / (v + m)

    popular.drop(columns="avg_rating", inplace=True)
    popular.drop(columns="count_rating", inplace=True)
    MOVIES = MOVIES.merge(popular, on='title')
    print("update_top10")
    return popular.sort_values('w_score', ascending=False).head(10)


def get_user_movies():
    global MOVIES_RATING

    active_users = MOVIES_RATING[MOVIES_RATING['userId'].map(MOVIES_RATING['userId'].value_counts()) > count_points]

    users_pivot = active_users.pivot_table(index=["userId"], columns=["title"], values="rating")
    users_pivot.fillna(0, inplace=True)
    print("get_user_movies")
    return users_pivot


def get_movie_recommendations(movie_title, users_pivot, num_recommendations=5):
    # Создаем экземпляр модели
    model_knn_movies = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=5, n_jobs=-1)

    # Переворачиваем матрицу, чтобы строки соответствовали фильмам, а столбцы пользователям
    movies_pivot_array = users_pivot.T.values

    # Обучаем модель
    model_knn_movies.fit(movies_pivot_array)

    # Получаем индексы и расстояния к похожим фильмам для каждого фильма
    movie_distances, movie_indices = model_knn_movies.kneighbors(movies_pivot_array)

    movie_index = users_pivot.columns.get_loc(movie_title)
    movie_distances_single = movie_distances[movie_index]
    movie_indices_single = movie_indices[movie_index]

    # Исключаем выбранный фильм из рекомендаций
    movie_distances_single = movie_distances_single[1:]
    movie_indices_single = movie_indices_single[1:]

    # Получаем индексы фильмов с наивысшими взвешенными рейтингами
    top_movie_indices = np.argsort(movie_distances_single)[:num_recommendations]

    # Выводим рекомендации
    recommended_movies = users_pivot.columns[movie_indices_single[top_movie_indices]]

    recommendations_df = pd.DataFrame({
        'title': recommended_movies
    })
    recommendations_df = recommendations_df.merge(MOVIES, on='title')
    recommendations_df.drop(columns="movieId", inplace=True)
    recommendations_df.drop(columns="genres", inplace=True)

    print("get_movie_recommendations")

    return recommendations_df.head(10)


def get_movie_from_genre(name_genre):
    genres = {"movieId": [], "genres": [], "w_score": [], "title": []}
    for index, row in MOVIES.iterrows():
        a = row["genres"].split("|")
        for j in a:
            genres["movieId"].append(row["movieId"])
            genres["genres"].append(j)
            genres["w_score"].append(row["w_score"])
            genres["title"].append(row["title"])

    movies_g = pd.DataFrame(genres)
    movies_g = movies_g.merge(RATING, on='movieId')

    avg_ratings = movies_g[movies_g['genres'].str.contains(name_genre)].groupby('title')[
        "rating"].mean().reset_index().rename(columns={'rating': 'avg_rating'})  # средняя оценка фильма
    cnt_ratings = movies_g[movies_g['genres'].str.contains(name_genre)].groupby('title')[
        'rating'].count().reset_index().rename(columns={'rating': 'count_rating'})  # кол-во оценок
    popularite = avg_ratings.merge(cnt_ratings, on='title')
    popularite.sort_values('count_rating', ascending=False).head()
    v = popularite["count_rating"]
    R = popularite["avg_rating"]
    m = v.quantile(quantile)
    c = R.mean()

    popularite['w_score'] = ((v * R) + (m * c)) / (v + m)
    popularite.drop(columns="avg_rating", inplace=True)
    popularite.drop(columns="count_rating", inplace=True)

    print("get_movie_from_genre")
    return popularite.head(10)

loading() # обезательно
update_movies_rating() # обезательно
# update_top10()

print(update_top10()) # обновить рейтинг
print(get_movie_recommendations("Shawshank Redemption, The (1994)" , get_user_movies())) # получить по фильму
print(get_movie_from_genre("Animation"))