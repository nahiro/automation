import os
import sys
import tkinter as tk
from tkinter import ttk

pnams = []
pnams.append('ref_fnam')
pnams.append('trg_fnam')
pnams.append('ref_pixel')
pnams.append('trg_binning')
params = {}
params['ref_fnam'] = 'Reference Image'
params['trg_fnam'] = 'Orthomosaic Image'
params['ref_pixel'] = 'Reference Pixel Size'
params['trg_binning'] = 'Target Binning Number'
param_types = {}
param_types['ref_fnam'] = 'string'
param_types['trg_fnam'] = 'string'
param_types['ref_pixel'] = 'double'
param_types['trg_binning'] = 'int'
defaults = {}
defaults['ref_fnam'] = 'wv2_180629_pan.tif'
defaults['trg_fnam'] = 'test.tif'
defaults['ref_pixel'] = 0.2
defaults['trg_binning'] = 8
defaults['boundary_width'] = 0.6
values = {}
for pnam in pnams:
    values[pnam] = defaults[pnam]
input_types = {}
input_types['ref_fnam'] = 'box'
input_types['trg_fnam'] = 'box'
input_types['ref_pixel'] = 'box'
input_types['trg_binning'] = 'box'

entry_width = 160
inidir = os.path.join(os.environ.get('USERPROFILE'),'Work','Drone')
browse_image = os.path.join(os.environ.get('USERPROFILE'),'Pictures','browse.png')

child_win = None
main_win = None
main_frm = None

def ask_folder(pnam,dnam=inidir):
    path = tkfilebrowser.askopendirname(initialdir=dnam)
    if len(path) > 0:
        child_var[pnam].set(path)
        defaults[pnam] = path
    return

def ask_folders(pnam,dnam=inidir):
    dirs = list(tkfilebrowser.askopendirnames(initialdir=dnam))
    if len(dirs) > 0:
        path = ';'.join(dirs)
        child_var[pnam].set(path)
        defaults[pnam] = path
    return

def set(parent,frame):
    global main_win
    global main_frm
    global child_win
    global child_var
    global child_label
    global child_input
    global child_err

    if child_win is not None and child_win.winfo_exists():
        return
    main_win = parent
    main_frm = frame
    child_win = tk.Toplevel(parent)
    child_win.title('Geometric Correction')
    child_win.geometry('400x240')
    child_frm = ttk.Frame(child_win)
    child_frm.grid(column=0,row=0,sticky=tk.NSEW,padx=5,pady=10)

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
    for pnam in pnams:
        if input_types[pnam] == 'box':
            child_input[pnam] = ttk.Entry(child_win,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width); y += dy
        else:
            raise ValueError('Error, unsupported input type >>> '.format(input_types[pnam]))

    child_err = {}
    for pnam in pnams:
        child_err[pnam] = ttk.Label(child_win,text='ERROR',foreground='red')

    child_btn02 = ttk.Button(child_win,text='Set',command=modify)
    child_btn02.place(x=60,y=y)

    return

def get_input(pnam):
    return child_input[pnam].get()

def get_value(pnam):
    return values[pnam]

def check(source='input'):
    if source == 'input':
        get = get_input
    elif source == 'value':
        get = get_value
    else:
        raise ValueError('Error, source={}'.format(source))
    check_values = {}
    check_errors = {}
    pnam = 'ref_fnam'
    try:
        t = get(pnam)
        if not os.path.exists(t):
            raise IOError('Error in {}, no such file >>> {}'.format(params[pnam],t))
        check_values[pnam] = t
        check_errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        check_values[pnam] = None
        check_errors[pnam] = True
    pnam = 'trg_fnam'
    try:
        t = get(pnam)
        if not os.path.exists(t):
            raise IOError('Error in {}, no such file >>> {}'.format(params[pnam],t))
        check_values[pnam] = t
        check_errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        check_values[pnam] = None
        check_errors[pnam] = True
    pnam = 'ref_pixel'
    try:
        t = get(pnam)
        v = float(t)
        if v < 0.01 or v > 50.0:
            raise ValueError('Error in {}, out of range >>> {}'.format(params[pnam],t))
        check_values[pnam] = v
        check_errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        check_values[pnam] = None
        check_errors[pnam] = True
    pnam = 'trg_binning'
    try:
        t = get(pnam)
        n = int(t)
        if n < 1 or n > 64:
            raise ValueError('Error in {}, out of range >>> {}'.format(params[pnam],t))
        check_values[pnam] = n
        check_errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        check_values[pnam] = None
        check_errors[pnam] = True
    if source == 'input':
        x0 = 320
        y0 = 15
        dy = 25
        y = y0
        for pnam in pnams:
            if check_errors[pnam]:
                child_err[pnam].place(x=x0,y=y); y += dy
            else:
                child_err[pnam].place_forget(); y += dy
    return check_values,check_errors

def modify():
    check_values,check_errors = check(source='input')
    err = False
    for pnam in pnams:
        value = check_values[pnam]
        error = check_errors[pnam]
        if error:
            err = True
        else:
            values[pnam] = value
    if not err:
        child_win.destroy()
    return

def run():
    sys.stderr.write('Running process 02.\n')
