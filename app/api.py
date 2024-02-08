from flask import Flask, jsonify, request
from flask_restful import Api
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

MOVIES = pd.DataFrame()
RATING = pd.DataFrame()
MOVIES_RATING = pd.DataFrame()
USERS_PIVOT = []

quantile = 0.9
count_points = 198
count_head = 10


def loading():
    global MOVIES, RATING
    MOVIES = pd.read_csv(r"movies.csv")
    RATING = pd.read_csv(r"rating.csv")
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
    if "w_score" in MOVIES.columns:
        MOVIES.drop(columns="w_score", inplace=True)
    MOVIES = MOVIES.merge(popular, on='title')
    print("update_top10")
    return popular.sort_values('w_score', ascending=False).head(count_head)


def update_user_movies():
    global MOVIES_RATING

    active_users = MOVIES_RATING[MOVIES_RATING['userId'].map(MOVIES_RATING['userId'].value_counts()) > count_points]

    users_pivot = active_users.pivot_table(index=["userId"], columns=["title"], values="rating")
    users_pivot.fillna(0, inplace=True)
    print("get_user_movies")
    return users_pivot


def update_movie_recommendations(movie_title, users_pivot, num_recommendations=5):
    update_top10()
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

    return recommendations_df.head(count_head)


def update_movie_from_genre(name_genre):
    update_top10()
    genres = {"movieId": [], "genres": [], "w_score": [], "title": []}
    for index, row in MOVIES.iterrows():
        a = row["genres"].split("|")
        for j in a:
            genres["movieId"].append(row["movieId"])
            genres["genres"].append(j.lower())
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
    return popularite.head(count_head)


@app.route('/top', methods=['GET'])
def get_top():
    top10 = update_top10()
    result = [{'title': row["title"], 'w_score': row['w_score']} for index, row in top10.iterrows()]
    return jsonify({'Топ 10 фильмов': result})


@app.route('/genre/<name_genre>', methods=['GET'])
def get_genre_name(name_genre):

    genre10 = update_movie_from_genre(name_genre)

    if len(genre10) < 1:
        return jsonify({'message': 'Genre not found'})

    result = [{'title': row["title"], 'w_score': row['w_score']} for index, row in genre10.iterrows()]
    return jsonify({name_genre: result})


@app.route('/movie/<name_movie>', methods=['GET'])
def get_movie_name(name_movie):

    movie10 = update_movie_recommendations(name_movie, update_user_movies())

    if len(movie10) < 1:
        return jsonify({'message': 'Movie not found'})

    result = [{'title': row["title"], 'w_score': row['w_score']} for index, row in movie10.iterrows()]
    return jsonify({"Рекомедации по фильму: " + name_movie: result})



if __name__ == '__main__':
    loading()  # обезательно
    update_movies_rating()  # обезательно
    api = Api(app)

    app.run(debug=True, host='0.0.0.0', port=5000)


# loading() # обезательно
# update_movies_rating() # обезательно
# update_top10()
# #
# # # print(update_top10()) # обновить рейтинг
# print(update_user_movies())
# print(update_movie_recommendations("Shawshank Redemption, The (1994)", update_user_movies())) # получить по фильму
# # print(update_movie_from_genre("Animation"))
