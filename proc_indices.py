import os
import sys
import tkinter as tk
from tkinter import ttk
import tkfilebrowser

proc_name = 'indices'
proc_title = 'Calculate Indices'
pnams = []
pnams.append('inp_fnam')
params = {}
params['inp_fnam'] = 'Input File'

child_win = None
main_win = None
main_frm = None
main_hid = None

def set(parent,frame):
    global main_win
    global main_frm
    global main_hid
    global child_win
    global child_var
    global child_label
    global child_input
    global child_browse
    global child_err

    if child_win is not None and child_win.winfo_exists():
        return
    main_win = parent
    main_frm = frame
    for x in main_frm.winfo_children():
        if isinstance(x,ttk.Button) and x['text'] == 'check_{}'.format(proc_name):
            main_hid = x
    child_win = tk.Toplevel(parent)
    child_win.title(proc_title)
    child_win.geometry('400x240')
    #browse_img = tk.PhotoImage(file=browse_image)

    child_cnv = tk.Canvas(child_win,width=400,height=240,background='yellow')
    child_cnv.pack()

    x0 = 30
    y0 = 15
    dy = 25
    y = y0
    child_label = {}
    for pnam in pnams:
        child_label[pnam] = ttk.Label(child_cnv,text=params[pnam])
        child_label[pnam].place(x=x0,y=y); y += dy
    
    return

def check(source='input'):
    return {},{}

def run():
    sys.stderr.write('Running process {}.\n'.format(proc_name))
