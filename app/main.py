import tkinter as tk
from tkinter import *
from tkinter import ttk
import json
import requests
import ctypes as ct
from tkinter.font import Font
from functools import partial
import re
import os
import pandas as pd

def top10():
    api_uri = ''
    movies = []
    movie_name = similar_movies_regex(list_column, entry.get())
    if(movie_name == 'None'):
        movies = [("", "")]
    else:
        api_uri = API_URL_movie + movie_name
        response = requests.get(api_uri)
        data = json.loads(response.content.decode('utf-8'))
        for movie in data:
            movies.append((movie[0], movie[1]))
        print(data)
        tree.bind('<B1-Motion>', partial(motion_handler, tree))
        motion_handler(tree, None)   

def similar_movies_regex(movie_list, regex_pattern):
    regex_pattern = re.compile(regex_pattern, re.IGNORECASE)
    for movie in movie_list:
        match = regex_pattern.search(movie)
        if match:
            return movie
    return 'None'


def createMainWindow():
    pass

def createChooseGenreWindow():
    root.withdraw()


    chooseWindow = tk.Toplevel()
    frm = ttk.Frame(chooseWindow, padding=10)
    chooseWindow.geometry('440x310+200+102')

    red_frame = Frame(chooseWindow, bg="#CA1F3D")
    red_frame.place(x=0.0, y=0.3, relwidth=1.0, relheight=0.3)

    black_frame = Frame(chooseWindow, bg="#25182E")
    black_frame.place(x=0, rely=0.3, relwidth=1.0, relheight=0.7)

    label_Main = tk.Label(chooseWindow,
                          text="Главная",
                          bg='#CA1F3D',
                          fg='#fff',
                          font='Helvetica 16 bold')

    label_Main.grid(column=0, row=0, padx=6, pady=9, sticky="w")

    label_Recommendation = tk.Label(chooseWindow,
                                    text="Рекомендации по фильму",
                                    bg='#CA1F3D',
                                    fg='#fff',
                                    font='Helvetica 9')

    label_Recommendation.grid(row=1, column=0, padx=9, pady=6, sticky="w")

    loadimage = PhotoImage(file='button_to_genres.png')
    button_TransitionToGenres = Button(chooseWindow, image=loadimage)
    button_TransitionToGenres["bg"] = "#CA1F3D"
    button_TransitionToGenres["border"] = "0"
    button_TransitionToGenres.grid(column=1, row=0, padx=0)

    button_TransitionToGenres.config(text="К жанрам", fg="white")

    data = [
        ("Inception", "8.8"),
        ("The Dark Knight", "9.0"),
        ("Toy Story", "8.3"),
        ("Interstellar", "8.6"),
        ("Pirates of the Caribbean", "7.9"),
    ]

    tree = ttk.Treeview(show='', columns=('title', 'rating'))
    tree.column('#0', width=0, stretch=NO)
    tree.column('title', anchor=CENTER, width=90)
    tree.column('rating', anchor=E, width=50)


    for item in data:
        tree.insert('', 'end', text='Inception', values=item)
    tree.grid(column=0, row=2, padx=0, pady=40)

    tree.bind('<B1-Motion>', partial(motion_handler, tree))
    motion_handler(tree, None)  # Perform initial wrapping

    chooseWindow.mainloop()

def motion_handler(tree, event):
    f = Font(font='TkDefaultFont')
    # A helper function that will wrap a given value based on column width
    def adjust_newlines(val, width, pad=0):
        if not isinstance(val, str):
            return val
        else:
            words = val.split()
            lines = [[],]
            for word in words:
                line = lines[-1] + [word,]
                if f.measure(' '.join(line)) < (width - pad):
                    lines[-1].append(word)
                else:
                    lines[-1] = ' '.join(lines[-1])
                    lines.append([word,])

            if isinstance(lines[-1], list):
                lines[-1] = ' '.join(lines[-1])

            return '\n'.join(lines)

    if (event is None) or (tree.identify_region(event.x, event.y) == "separator"):
        # You may be able to use this to only adjust the two columns that you care about
        # print(tree.identify_column(event.x))

        col_widths = [tree.column(cid)['width'] for cid in tree['columns']]

        for iid in tree.get_children():
            new_vals = []
            for (v,w) in zip(tree.item(iid)['values'], col_widths):
                new_vals.append(adjust_newlines(v, w))
            tree.item(iid, values=new_vals)



current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

csv_path = current_dir + '\movies.csv'
df = pd.read_csv(csv_path)
column = df['title']
list_column = list(column)


API_URL_top = "http://192.168.138.222:5000/top"
API_URL_movie = "http://127.0.0.1:5000/movie/"


# НАЧАЛО РАБОТЫ С ГЛАВНЫМ ОКНОМ 


root = tk.Tk()
frm = ttk.Frame(root, padding=10)
root.geometry('440x310+200+102')

red_frame = Frame(root, bg="#CA1F3D")
red_frame.place(x=0.0, y=0.3, relwidth=1.0, relheight=0.3)

black_frame = Frame(root, bg="#25182E")
black_frame.place(x=0, rely=0.3, relwidth=1.0, relheight=0.7)


label_Main = tk.Label(root, 
                text="Главная", 
                bg = '#CA1F3D', 
                fg='#fff', 
                font='Helvetica 16 bold')

label_Main.grid(column=0, row=0, padx=6, pady=9,  sticky="w")

label_Recommendation = tk.Label(root, 
                    text="Рекомендации по фильму",  
                    bg = '#CA1F3D', 
                    fg='#fff', 
                    font='Helvetica 9')

label_Recommendation.grid(row=1, column=0, padx=9, pady=6, sticky="w")

entry  = ttk.Entry(root)
entry.grid(column=1, row=1, padx=0, sticky='w')

button_searcher = tk.Button(root, text='поиск', command = top10)
button_searcher.grid(column=2, row=1, padx=0, sticky='w')

loadimage = tk.PhotoImage(file="button_to_genres.png")
button_TransitionToGenres = tk.Button(root, image=loadimage, command=createChooseGenreWindow)
button_TransitionToGenres["bg"] = "#CA1F3D"
button_TransitionToGenres["border"] = "0"
button_TransitionToGenres.grid(column=1, row=0, padx=0)

button_TransitionToGenres.config(text="К жанрам", fg="white")









tree = ttk.Treeview(show='', columns=('title', 'rating'))
tree.column('#0', width=0, stretch=NO)
tree.column('title', anchor=CENTER, width=90)
tree.column('rating', anchor=E, width=50)



tree.grid(column=0, row=2, padx=0, pady=40)



root.mainloop()


def find():
    pass

def getTop_movie_info():
    response = requests.get(API_URL_top)
    if response.status_code != 200:
        return None
    movies = json.loads(response.content.decode('utf-8'))
    return movies

def get_movie_info(movie_name):
    response = requests.get(API_URL_movie + '{' + movie_name + '}')
    if response.status_code != 200:
        return None
    movies = json.loads(response.content.decode('utf-8'))
    return movies






