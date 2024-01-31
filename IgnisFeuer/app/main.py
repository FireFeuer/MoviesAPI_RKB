import tkinter as tk
from tkinter import *
from tkinter import ttk
import json
import ctypes as ct




API_URL_top = "http://192.168.138.222:5000/top"
API_URL_movie = "http://192.168.138.222:5000/movie/"


# НАЧАЛО РАБОТЫ С ГЛАВНЫМ ОКНОМ 

root = tk.Tk()
frm = ttk.Frame(root, padding=10)
root.geometry('440x310+200+102')

red_frame = Frame(root, bg="#CA1F3D")
red_frame.place(x=0.0, y=0.3, relwidth=1.0, relheight=0.3)

black_frame = Frame(root, bg="#25182E")
black_frame.place(x=0, rely=0.3, relwidth=1.0, relheight=0.7)

# КОНЕЦ РАБОТЫ С ГЛАВНЫМ ОКНОМ


# НАЧАЛО РАБОТЫ С ЭЛЕМЕНТАМИ ГЛАВНОГО ОКНА 

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


loadimage = tk.PhotoImage(file="button_k-zhanram.png")
button_TransitionToGenres = tk.Button(root, image=loadimage)
button_TransitionToGenres["bg"] = "#CA1F3D"
button_TransitionToGenres["border"] = "0"
button_TransitionToGenres.grid(column=1, row=0, padx=150)

button_TransitionToGenres.config(text="К жанрам", fg="white")


data = [
("1", "Inception", "8.8", "star.jpg"),
("2", "The Dark Knight", "9.0", "star.jpg"),
("3", "Toy Story", "8.3", "star.jpg"),
("4", "Interstellar", "8.6", "star.jpg"),
("5", "Pirates of the Caribbean", "7.9", "star.jpg"),
]

tree = ttk.Treeview(show='', columns=('number', 'title', 'rating', 'icon'))
tree.column('#0', width=0, stretch=NO)
tree.column('number', anchor=CENTER, width=80)
tree.column('title', anchor=CENTER, width=80)
tree.column('rating', anchor=CENTER, width=80)
tree.column('icon', anchor=CENTER, width=80)

for item in data:
    tree.insert('', 'end', text='Inception', values = item)
tree.grid(column=0, row=2, padx=0, pady=20)


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

