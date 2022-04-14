import os
import sys
import tkinter as tk
from tkinter import ttk
import tkfilebrowser

proc_name = 'indices'
proc_title = 'Calculate Indices'

def set(parent,frame):
    child_win = tk.Canvas(parent,width=400,height=240)
    #child_win.title(proc_title)
    #child_win.geometry('400x240')
    
    return

def check(source='input'):
    return {},{}

def run():
    sys.stderr.write('Running process {}.\n'.format(proc_name))
