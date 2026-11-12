import tkinter as tk
from tkinter import ttk


root = tk.Tk()
root.title("MicroLearning Builder")

slides = tk.Listbox(root,width=25)
slides.pack(side="left",fill="y")

editor = tk.Text(root)
editor.pack(side="left",fill="both",expand=True)

root.mainloop()