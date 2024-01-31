import tkinter as tk
from tkinter import *
from tkinter import ttk
import requests
import json
import ctypes as ct

API_URL_top = "http://192.168.138.222:5000/top"
API_URL_movie = "http://192.168.138.222:5000/movie/"


root = tk.Tk()
frm = ttk.Frame(root, padding=10)

root.geometry('429x276+200+102')

search_var = tk.StringVar(root)

red_frame = Frame(root, bg="#CA1F3D")
red_frame.place(x=0.0, y=0.3, relwidth=1.0, relheight=0.3)

black_frame = Frame(root, bg="#25182E")
black_frame.place(x=0, rely=0.3, relwidth=1.0, relheight=0.7)

label = tk.Label(root, text="Главная", bg = '#CA1F3D', fg='#fff', font='Helvetica 16 bold')
label.grid(column=0, row=0, padx=20, pady=9)

label = tk.Label(root, text="Рекомендации по фильму", bg = '#CA1F3D', fg='#fff', font='Helvetica 8')
label.grid(row=1, column=0, padx=6, pady=2)

button = tk.Button(root,
                   font="Helvetica 10 bold",
                   bg="yellow",
                   activebackground="gold",
                   relief="raised",
                   )
button.grid(column=1, row=0, padx=199)

button.config(text="К жанрам", fg="white")


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

def dark_title_bar(window):
    window.update()
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, 20, ct.byref(value),
                         4)