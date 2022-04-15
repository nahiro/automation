import os
import sys
import tkinter as tk
from tkinter import ttk
import tkfilebrowser

proc_name = 'output'
proc_title = 'Output Results'

def set(parent,canvas):
    child = tk.Toplevel(parent)
    child.geometry('400x200')
    return

def check(source='input'):
    return {},{}

def run():
    sys.stderr.write('Running process {}.\n'.format(proc_name))
