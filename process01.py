import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkfilebrowser

pnams = []
pnams.append('inpdirs')
pnams.append('outdir')
params = {}
params['inpdirs'] = 'Input Folders'
params['outdir'] = 'Output Folder'
param_types = {}
param_types['inpdirs'] = 'string'
param_types['outdir'] = 'string'
defaults = {}
defaults['inpdirs'] = 'input'
defaults['outdir'] = 'output'
input_types = {}
input_types['inpdirs'] = 'askfolders'
input_types['outdir'] = 'askfolder'

entry_width = 160
button_width = 20
button_height = 21

def ask_folder():
    path = tkfilebrowser.askopendirname(initialdir=os.getcwd())
    if len(path) > 0:
        child01_var['outdir'].set(path)
        defaults['outdir'] = path
    return

def ask_folders():
    dirs = list(tkfilebrowser.askopendirnames(initialdir=os.getcwd()))
    if len(dirs) > 0:
        path = ';'.join(dirs)
        child01_var['inpdirs'].set(path)
        defaults['inpdirs'] = path
    return

def set(parent):
    global child01_win
    global child01_var
    global child01_label
    global child01_input
    global child01_browse
    global child01_err

    child01_win = tk.Toplevel(parent)
    child01_win.title('Make Orthomosaic')
    child01_win.geometry('400x240')
    child01_frm = ttk.Frame(child01_win)
    child01_frm.grid(column=0,row=0,sticky=tk.NSEW,padx=5,pady=10)
    browse_img = tk.PhotoImage(file='browse.png')

    child01_var = {}
    for pnam in pnams:
        if param_types[pnam] == 'string':
            child01_var[pnam] = tk.StringVar()
        elif param_types[pnam] == 'int':
            child01_var[pnam] = tk.IntVar()
        elif param_types[pnam] == 'double':
            child01_var[pnam] = tk.DoubleVar()
        elif param_types[pnam] == 'boolean':
            child01_var[pnam] = tk.BooleanVar()
        else:
            raise ValueError('Error, unsupported parameter type >>> '.format(param_types[pnam]))
        child01_var[pnam].set(defaults[pnam])

    x0 = 30
    y0 = 15
    dy = 25
    y = y0
    child01_label = {}
    for pnam in pnams:
        child01_label[pnam] = ttk.Label(child01_win,text=params[pnam])
        child01_label[pnam].place(x=x0,y=y); y += dy

    x0 = 160
    y0 = 15
    dy = 25
    y = y0
    child01_input = {}
    child01_browse = {}
    for pnam in pnams:
        if input_types[pnam] == 'box':
            child01_input[pnam] = ttk.Entry(child01_win,textvariable=child01_var[pnam])
            child01_input[pnam].place(x=x0,y=y,width=entry_width); y += dy
        elif input_types[pnam] == 'askfolder':
            child01_input[pnam] = ttk.Entry(child01_win,textvariable=child01_var[pnam])
            child01_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            child01_browse[pnam] = tk.Button(child01_win,image=browse_img,bg='white',bd=1,command=ask_folder)
            child01_browse[pnam].image = browse_img
            child01_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        elif input_types[pnam] == 'askfolders':
            child01_input[pnam] = ttk.Entry(child01_win,textvariable=child01_var[pnam])
            child01_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            child01_browse[pnam] = tk.Button(child01_win,image=browse_img,bg='white',bd=1,command=ask_folders)
            child01_browse[pnam].image = browse_img
            child01_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        else:
            raise ValueError('Error, unsupported input type >>> '.format(input_types[pnam]))

    child01_err = {}
    for pnam in pnams:
        child01_err[pnam] = ttk.Label(child01_win,text='ERROR',foreground='red')

    child01_btn01 = ttk.Button(child01_win,text='Set',command=modify)
    child01_btn01.place(x=60,y=y)

    return

def check():
    values = {}
    errors = {}
    pnam = 'inpdirs'
    try:
        t = child01_input[pnam].get()
        for item in t.split(';'):
            if not os.path.isdir(item):
                raise IOError('Error in {}, no such folder >>> {}'.format(params[pnam],item))
        values[pnam] = t
        errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        values[pnam] = None
        errors[pnam] = True
    pnam = 'outdir'
    try:
        t = child01_input[pnam].get()
        if not os.path.exists(t):
            os.makedirs(t)
        if not os.path.isdir(t):
            raise IOError('Error in {}, no such folder >>> {}'.format(params[pnam],t))
        values[pnam] = t
        errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        values[pnam] = None
        errors[pnam] = True
    x0 = 320
    y0 = 15
    dy = 25
    y = y0
    for pnam in pnams:
        if errors[pnam]:
            child01_err[pnam].place(x=x0,y=y); y += dy
        else:
            child01_err[pnam].place_forget(); y += dy
    return values,errors

def modify():
    values,errors = check()
    err = False
    for pnam in pnams:
        value = values[pnam]
        error = errors[pnam]
        if error:
            err = True
    if not err:
        child01_win.destroy()
    return

def run():
    sys.stderr.write('Running process 01.\n')
