from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, \
    QWidget, QGridLayout, QComboBox,  QScrollArea
from PyQt5.QtCore import Qt
import pandas as pd
import requests
import sys
import re


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Главное окно")
        self.setGeometry(100, 100, 700, 500)
        self.movies_data = get_data()
        self.init_ui()

    def init_ui(self):
        # Шапка
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #CA1F3D;")
        header_layout = QHBoxLayout(header_widget)

        button_question = QPushButton("I", self)
        button_question.setStyleSheet("background-color: #FFBE00; border: none; padding: 5px; border-radius: 2px;")
        button_question.clicked.connect(self.open_question_window)
        header_layout.addWidget(button_question, alignment=Qt.AlignLeft)
        self.dialog2 = QuestionWindow(self)

        label_main = QLabel("Главная", self)
        label_main.setStyleSheet("color: white; font-size: 34px; padding: 10px;")
        header_layout.addWidget(label_main)

        # Label "Рекомендации по фильму" в центре шапки
        label_recommendations_header = QLabel("Рекомендации по фильму", self)
        label_recommendations_header.setStyleSheet("color: white; font-size: 12px; margin: 10px;")
        header_layout.addWidget(label_recommendations_header)

        # Строка поиска с белой линией в шапке
        self.entry_search = QLineEdit(self)
        self.entry_search.setStyleSheet(
            "border: 2px solid white; border-radius: 5px; padding: 5px; font-size: 12px; color: white;")
        self.entry_search.textChanged.connect(self.on_text_changed)  # Подключаем событие textChanged
        header_layout.addWidget(self.entry_search)

        # Выпадающее меню (QComboBox)
        self.combo_box = QComboBox(self)
        self.combo_box.setStyleSheet(
            "border: 2px solid white; border-radius: 5px; padding: 5px; font-size: 12px; color: white;")
        header_layout.addWidget(self.combo_box)

        # Кнопка поиска с лупой в шапке
        button_search = QPushButton("🔍", self)
        button_search.setStyleSheet(
            "background-color: #CA1F3D; color: white; border: none; padding: 5px; border-radius: 5px;")
        button_search.clicked.connect(self.search_movie)
        header_layout.addWidget(button_search)

        button_genres = QPushButton("К жанрам", self)
        button_genres.setStyleSheet("background-color: #FFBE00; border: none; padding: 10px; border-radius: 5px;")
        button_genres.clicked.connect(self.open_genres_window)
        self.dialog = GenresWindow(self)

        header_layout.addWidget(button_genres, alignment=Qt.AlignRight)
        # Главное вертикальное расположение
        main_layout = QVBoxLayout()

        # Создаем виджет для отображения фильмов
        self.movies_widget = QWidget(self)
        self.movies_widget.setStyleSheet("background-color: #25182E;")
        self.movies_layout = QGridLayout(self.movies_widget)
        self.movies_layout.setContentsMargins(0, 0, 0, 0)

        self.top10_view()

        main_layout.addWidget(header_widget)
        main_layout.addWidget(self.movies_widget, 2)  # 2/3 нижней части окна
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.combo_box.setFixedWidth(150)
        self.combo_box.view().setFixedWidth(300)
        self.setCentralWidget(central_widget)

    def top10_view(self):
        # Данные с API
        api_data = self.get_api_data()

        # Заголовок
        self.title_label = QLabel("Топ 10 фильмов", self)
        self.title_label.setStyleSheet("color: white; font-size: 18px; padding: 10px;")
        self.movies_layout.addWidget(self.title_label, 0, 0, 1, 4, alignment=Qt.AlignCenter)

        row, col = 1, 0
        for i, movie in enumerate(api_data["Топ 10 фильмов"]):
            movie_label = QLabel(f"{i + 1}. {movie['title']}", self)
            movie_label.setStyleSheet(
                "background-color: white; color: #25182E; padding: 10px; margin: 5px; border-radius: 5px;")
            movie_label.setFixedHeight(50)
            self.movies_layout.addWidget(movie_label, row, col)

            score_label = QLabel(f"{movie['w_score']:.2f}", self)
            score_label.setStyleSheet(
                "background-color: #FFBE00; color: #25182E; padding: 10px; margin: 5px; border-radius: 5px;")
            score_label.setAlignment(Qt.AlignCenter)
            score_label.setFixedHeight(50)
            score_label.setFixedWidth(50)
            self.movies_layout.addWidget(score_label, row, col + 1)

            col += 2
            if col >= 4:
                col = 0
                row += 1

    def open_genres_window(self):
        self.hide()
        self.dialog.show()

    def open_question_window(self):
        self.hide()
        self.dialog2.show()

    def search_movie(self):
        # Метод, который вызывается при нажатии на кнопку поиска
        selected_movie = self.combo_box.currentText()
        api_url = f"http://127.0.0.1:5000/movie/{selected_movie}"
        response = requests.get(api_url)

        if response.status_code == 200:
            json_data = response.json()

            # Очищаем виджет с фильмами
            for i in reversed(range(self.movies_layout.count())):
                widget = self.movies_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)

            self.title_label.setText(f"Рекомедации по фильму: {selected_movie}")
            self.movies_layout.addWidget(self.title_label, 0, 0, 1, 4, alignment=Qt.AlignCenter)
            # Добавляем новые данные из JSON
            row, col = 1, 0
            for i, movie in enumerate(json_data[f"Рекомедации по фильму: {selected_movie}"]):
                movie_label = QLabel(f"{i + 1}. {movie['title']}", self)
                movie_label.setStyleSheet(
                    "background-color: white; color: #25182E; padding: 10px; margin: 5px; border-radius: 5px;")
                movie_label.setFixedHeight(50)
                self.movies_layout.addWidget(movie_label, row, col)

                score_label = QLabel(f"{movie['w_score']:.2f}", self)
                score_label.setStyleSheet(
                    "background-color: #FFBE00; color: #25182E; padding: 10px; margin: 5px; border-radius: 5px;")
                score_label.setAlignment(Qt.AlignCenter)
                score_label.setFixedHeight(50)
                score_label.setFixedWidth(50)
                self.movies_layout.addWidget(score_label, row, col + 1)

                col += 2
                if col >= 4:
                    col = 0
                    row += 1
        else:
            print(f"Ошибка при обращении к API. Статус код: {response.status_code}")

    def get_api_data(self):
        # Запрос данных с API
        url = "http://127.0.0.1:5000/top"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            return {"Топ 10 фильмов": []}

    def on_text_changed(self, text):
        # Этот метод будет вызываться при изменении текста в поле ввода
        # Находим подходящие строки в DataFrame MOVIES и добавляем их названия в QComboBox
        if not text:
            # Очищаем виджет с фильмами
            for i in reversed(range(self.movies_layout.count())):
                widget = self.movies_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)
            self.combo_box.clear()
            self.top10_view()
        else:
            # Экранируем спецсимволы в тексте
            escaped_text = re.escape(text.strip())
            matching_titles = MOVIES[MOVIES['title'].str.contains(escaped_text, case=False)]['title']
            self.combo_box.clear()
            self.combo_box.addItems(matching_titles)


class GenresWindow(QMainWindow):
    def __init__(self, parent=None):
        super(GenresWindow, self).__init__(parent)
        self.setWindowTitle("Окно жанров")
        self.setGeometry(100, 100, 700, 500)
        self.movies_data = get_data()
        self.init_ui()

    def init_ui(self):
        # Шапка
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #CA1F3D;")
        header_layout = QHBoxLayout(header_widget)

        label_main = QLabel("Жанры", self)
        label_main.setStyleSheet("color: white; font-size: 34px; padding: 10px;")
        header_layout.addWidget(label_main)

        # Label "Рекомендации по фильму" в центре шапки
        label_recommendations_header = QLabel("Рекомендации по жанру", self)
        label_recommendations_header.setStyleSheet("color: white; font-size: 12px; margin: 10px;")
        header_layout.addWidget(label_recommendations_header)

        # Строка поиска с белой линией в шапке
        self.entry_search = QLineEdit(self)
        self.entry_search.setStyleSheet(
            "border: 2px solid white; border-radius: 5px; padding: 5px; font-size: 12px; color: white;")
        self.entry_search.textChanged.connect(self.on_text_changed)  # Подключаем событие textChanged
        header_layout.addWidget(self.entry_search)

        # Кнопка поиска с лупой в шапке
        button_search = QPushButton("🔍", self)
        button_search.setStyleSheet(
            "background-color: #CA1F3D; color: white; border: none; padding: 5px; border-radius: 5px;")
        button_search.clicked.connect(self.search_movie)
        header_layout.addWidget(button_search)

        button_main = QPushButton("На главную", self)
        button_main.setStyleSheet("background-color: #FFBE00; border: none; padding: 10px; border-radius: 5px;")
        button_main.clicked.connect(self.open_main_window)
        self.dialog = self.parent()

        header_layout.addWidget(button_main, alignment=Qt.AlignRight)

        # Главное вертикальное расположение
        main_layout = QVBoxLayout()

        # Создаем виджет для отображения фильмов
        self.movies_widget = QWidget(self)
        self.movies_widget.setStyleSheet("background-color: #25182E;")
        self.movies_layout = QGridLayout(self.movies_widget)
        self.movies_layout.setContentsMargins(0, 0, 0, 0)
        self.genres_view()
        main_layout.addWidget(header_widget)
        main_layout.addWidget(self.movies_widget, 2)  # 2/3 нижней части окна
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def genres_view(self):
        # Получаем список всех жанров из данных фильмов
        genres = []
        for index, row in self.movies_data.iterrows():
            genres.extend(row["genres"].split("|"))

        # Удаляем дубликаты жанров и преобразуем в нижний регистр
        unique_genres = list(set(genres))
        unique_genres.sort()  # Сортируем жанры по алфавиту

        # Очищаем существующие виджеты
        for i in reversed(range(self.movies_layout.count())):
            widget = self.movies_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Отображаем все жанры в два столбца с использованием QScrollArea
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_layout = QGridLayout(scroll_widget)

        row, col = 1, 0
        for i, genre in enumerate(unique_genres):
            genre_button = QPushButton(genre, self)
            genre_button.setStyleSheet(
                "background-color: white; color: #25182E; padding: 10px; margin: 5px; border-radius: 5px;")
            genre_button.clicked.connect(
                lambda event, text=genre: self.on_genre_click(event, text))  # При нажатии выводим название жанра в консоль
            scroll_layout.addWidget(genre_button, row, col)

            col += 1
            if col == 2:
                col = 0
                row += 1

        self.movies_layout.addWidget(scroll_area, 1, 0, 1, 4)

    def on_genre_click(self, event, genre):
        # Метод вызывается при нажатии на плашку жанра
        self.entry_search.setText(genre.capitalize())
        self.search_movie()


    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def open_main_window(self):
        self.hide()
        self.dialog.show()

    def search_movie(self):
        # Метод, который вызывается при нажатии на кнопку поиска
        selected_genre = self.entry_search.text().lower()
        api_url = f"http://127.0.0.1:5000/genre/{selected_genre}"
        response = requests.get(api_url)

        if response.status_code == 200:
            json_data = response.json()

            # Очищаем виджет с фильмами
            for i in reversed(range(self.movies_layout.count())):
                widget = self.movies_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)

            self.title_label1 = QLabel("", self)
            self.title_label1.setStyleSheet("color: white; font-size: 34px; padding: 10px;")
            self.title_label1.setText(f"{selected_genre}")
            self.movies_layout.addWidget(self.title_label1, 0, 0, 1, 4, alignment=Qt.AlignCenter)
            # Добавляем новые данные из JSON
            row, col = 1, 0
            for i, movie in enumerate(json_data[f"{selected_genre}"]):
                movie_label = QLabel(f"{i + 1}. {movie['title']}", self)
                movie_label.setStyleSheet(
                    "background-color: white; color: #25182E; padding: 10px; margin: 5px; border-radius: 5px;")
                movie_label.setFixedHeight(50)
                self.movies_layout.addWidget(movie_label, row, col)

                score_label = QLabel(f"{movie['w_score']:.2f}", self)
                score_label.setStyleSheet(
                    "background-color: #FFBE00; color: #25182E; padding: 10px; margin: 5px; border-radius: 5px;")
                score_label.setAlignment(Qt.AlignCenter)
                score_label.setFixedHeight(50)
                score_label.setFixedWidth(50)
                self.movies_layout.addWidget(score_label, row, col + 1)

                col += 2
                if col >= 4:
                    col = 0
                    row += 1
        else:
            print(f"Ошибка при обращении к API. Статус код: {response.status_code}")

    def on_text_changed(self, text):
        # Этот метод будет вызываться при изменении текста в поле ввода
        # Находим подходящие строки в DataFrame MOVIES и добавляем их названия в QComboBox
        if not text:
            # Если строка поиска пуста, отображаем все жанры
            self.clear_layout(self.movies_layout)
            self.genres_view()
        else:
            # Если строка поиска не пуста, отображаем только подходящие жанры
            self.clear_layout(self.movies_layout)
            self.show_matching_genres(text)

    def show_matching_genres(self, text):
        # Получаем список всех жанров из данных о фильмах
        genres = []
        for index, row in self.movies_data.iterrows():
            a = row["genres"].split("|")
            for j in a:
                genres.append(j.lower())
        unique_genres = list(set(genres))

        # Фильтруем жанры в соответствии с введенным текстом
        filtered_genres = unique_genres
        if text:
            filtered_genres = [genre for genre in unique_genres if text.lower() in genre]

        # Создаем плашки для жанров и добавляем их в layout
        row, col = 1, 0
        for i, genre in enumerate(filtered_genres):
            genre_label = QLabel(genre.capitalize(), self)
            genre_label.setStyleSheet(
                "background-color: white; color: #25182E; padding: 10px; margin: 5px; border-radius: 5px;")
            genre_label.setFixedHeight(50)
            genre_label.setFixedWidth(150)
            genre_label.setAlignment(Qt.AlignCenter)
            self.movies_layout.addWidget(genre_label, row, col)
            genre_label.mousePressEvent = lambda event, text=genre: self.on_genre_click(event, text)

            col += 1
            if col >= 2:
                col = 0
                row += 1


class QuestionWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QuestionWindow, self).__init__(parent)
        self.setWindowTitle("Справка")
        self.setGeometry(100, 100, 700, 500)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        # Шапка
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #CA1F3D;")
        header_layout = QHBoxLayout(header_widget)

        label1 = QLabel("Справка")
        label1.setStyleSheet("color: #FFFFFF; font-size: 24px; ")
        header_layout.addWidget(label1)

        button1 = QPushButton("На главную")
        button1.setStyleSheet("background-color: #FFBE00; border: none; padding: 10px; border-radius: 5px;")
        button1.clicked.connect(self.open_main_window)
        header_layout.addWidget(button1, alignment=Qt.AlignRight)

        layout.addWidget(header_widget)

        # Тело
        body_widget = QWidget()
        body_widget.setStyleSheet("background-color: #25182E;")  # Черный фон
        body_layout = QVBoxLayout(body_widget)

        label2 = QLabel()
        label2.setText("О программе “Система рекомендаций фильмов”.\n\n"
                       "Приложение предназначено для поиска рекомендованных фильмов по названию или жанру.\n\n"
                       "Рекомендации по использованию.\n\n"
                       "    Для того чтобы получить рекомендации к фильму по названию необходимо:\n"
                       "На главной странице ввести название фильма в поисковую строку.\n"
                       "Выбрать нужный фильм из выпадающего списка.\n"
                       "Нажать на кнопку поиска(🔎).\n"
                       "   Для того чтобы получить рекомендации по фильму по жанру необходимо:\n"
                       "Перейти к окну со списком жанров по кнопке “к жанрам” на главной странице.\n"
                       "Ввести наименование жанра в поисковую строку.\n"
                       "Нажать на кнопку поиска(🔎)\n"
                       "Выбрать нужный жанр.")
        label2.setStyleSheet("color: #FFFFFF; font-size: 16px; padding: 5px")
        body_layout.addWidget(label2)

        layout.addWidget(body_widget, 2)  # Тело занимает 2/3 высоты окна

    def open_main_window(self):
        self.hide()
        self.parent().show()


MOVIES = []


def get_data():
    global MOVIES
    MOVIES = pd.read_csv(r"../data/movies.csv")
    return MOVIES


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
