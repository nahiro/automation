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

child_win = None

def ask_folder(pnam,dnam=os.getcwd()):
    path = tkfilebrowser.askopendirname(initialdir=dnam)
    if len(path) > 0:
        child_var[pnam].set(path)
        defaults[pnam] = path
    return

def ask_folders(pnam,dnam=os.getcwd()):
    dirs = list(tkfilebrowser.askopendirnames(initialdir=dnam))
    if len(dirs) > 0:
        path = ';'.join(dirs)
        child_var[pnam].set(path)
        defaults[pnam] = path
    return

def set(parent):
    global child_win
    global child_var
    global child_label
    global child_input
    global child_browse
    global child_err

    if child_win is not None and child_win.winfo_exists():
        return
    child_win = tk.Toplevel(parent)
    child_win.title('Make Orthomosaic')
    child_win.geometry('400x240')
    child_frm = ttk.Frame(child_win)
    child_frm.grid(column=0,row=0,sticky=tk.NSEW,padx=5,pady=10)
    browse_img = tk.PhotoImage(file='browse.png')

    child_var = {}
    for pnam in pnams:
        if param_types[pnam] == 'string':
            child_var[pnam] = tk.StringVar()
        elif param_types[pnam] == 'int':
            child_var[pnam] = tk.IntVar()
        elif param_types[pnam] == 'double':
            child_var[pnam] = tk.DoubleVar()
        elif param_types[pnam] == 'boolean':
            child_var[pnam] = tk.BooleanVar()
        else:
            raise ValueError('Error, unsupported parameter type >>> '.format(param_types[pnam]))
        child_var[pnam].set(defaults[pnam])

    x0 = 30
    y0 = 15
    dy = 25
    y = y0
    child_label = {}
    for pnam in pnams:
        child_label[pnam] = ttk.Label(child_win,text=params[pnam])
        child_label[pnam].place(x=x0,y=y); y += dy

    x0 = 160
    y0 = 15
    dy = 25
    y = y0
    child_input = {}
    child_browse = {}
    for pnam in pnams:
        if input_types[pnam] == 'box':
            child_input[pnam] = ttk.Entry(child_win,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width); y += dy
        elif input_types[pnam] == 'askfolder':
            child_input[pnam] = ttk.Entry(child_win,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            if pnam == 'outdir':
                child_browse[pnam] = tk.Button(child_win,image=browse_img,bg='white',bd=1,command=lambda:ask_folder('outdir'))
            else:
                raise ValueError('Error, pnam={}, input_types={}'.format(pnam,input_types[pnam]))
            child_browse[pnam].image = browse_img
            child_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        elif input_types[pnam] == 'askfolders':
            child_input[pnam] = ttk.Entry(child_win,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            if pnam == 'inpdirs':
                child_browse[pnam] = tk.Button(child_win,image=browse_img,bg='white',bd=1,command=lambda:ask_folders('inpdirs'))
            else:
                raise ValueError('Error, pnam={}, input_types={}'.format(pnam,input_types[pnam]))
            child_browse[pnam].image = browse_img
            child_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        else:
            raise ValueError('Error, unsupported input type >>> '.format(input_types[pnam]))

    child_err = {}
    for pnam in pnams:
        child_err[pnam] = ttk.Label(child_win,text='ERROR',foreground='red')

    child_btn01 = ttk.Button(child_win,text='Set',command=modify)
    child_btn01.place(x=60,y=y)

    return

def check():
    values = {}
    errors = {}
    pnam = 'inpdirs'
    try:
        t = child_input[pnam].get()
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
        t = child_input[pnam].get()
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
            child_err[pnam].place(x=x0,y=y); y += dy
        else:
            child_err[pnam].place_forget(); y += dy
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
        child_win.destroy()
    return

def run():
    sys.stderr.write('Running process 01.\n')
