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
input_types = {}
input_types['ref_fnam'] = 'box'
input_types['trg_fnam'] = 'box'
input_types['ref_pixel'] = 'box'
input_types['trg_binning'] = 'box'

entry_width = 160

def set(parent):
    global child02_win
    global child02_var
    global child02_label
    global child02_input
    global child02_err

    child02_win = tk.Toplevel(parent)
    child02_win.title('Geometric Correction')
    child02_win.geometry('400x240')
    child02_frm = ttk.Frame(child02_win)
    child02_frm.grid(column=0,row=0,sticky=tk.NSEW,padx=5,pady=10)

    child02_var = {}
    for pnam in pnams:
        if param_types[pnam] == 'string':
            child02_var[pnam] = tk.StringVar()
        elif param_types[pnam] == 'int':
            child02_var[pnam] = tk.IntVar()
        elif param_types[pnam] == 'double':
            child02_var[pnam] = tk.DoubleVar()
        elif param_types[pnam] == 'boolean':
            child02_var[pnam] = tk.BooleanVar()
        else:
            raise ValueError('Error, unsupported parameter type >>> '.format(param_types[pnam]))
        child02_var[pnam].set(defaults[pnam])

    x0 = 30
    y0 = 15
    dy = 25
    y = y0
    child02_label = {}
    for pnam in pnams:
        child02_label[pnam] = ttk.Label(child02_win,text=params[pnam])
        child02_label[pnam].place(x=x0,y=y); y += dy

    x0 = 160
    y0 = 15
    dy = 25
    y = y0
    child02_input = {}
    for pnam in pnams:
        if input_types[pnam] == 'box':
            child02_input[pnam] = ttk.Entry(child02_win,textvariable=child02_var[pnam])
            child02_input[pnam].place(x=x0,y=y,width=entry_width); y += dy
        else:
            raise ValueError('Error, unsupported input type >>> '.format(input_types[pnam]))

    child02_err = {}
    for pnam in pnams:
        child02_err[pnam] = ttk.Label(child02_win,text='ERROR',foreground='red')

    child02_btn02 = ttk.Button(child02_win,text='Set',command=modify)
    child02_btn02.place(x=60,y=y)

    return

def check():
    values = {}
    errors = {}
    pnam = 'ref_fnam'
    try:
        t = child02_input[pnam].get()
        if not os.path.exists(t):
            raise IOError('Error in {}, no such file >>> {}'.format(params[pnam],t))
        values[pnam] = t
        errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        values[pnam] = None
        errors[pnam] = True
    pnam = 'trg_fnam'
    try:
        t = child02_input[pnam].get()
        if not os.path.exists(t):
            raise IOError('Error in {}, no such file >>> {}'.format(params[pnam],t))
        values[pnam] = t
        errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        values[pnam] = None
        errors[pnam] = True
    pnam = 'ref_pixel'
    try:
        t = child02_input[pnam].get()
        v = float(t)
        if v < 0.01 or v > 50.0:
            raise ValueError('Error in {}, out of range >>> {}'.format(params[pnam],t))
        values[pnam] = v
        errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        values[pnam] = None
        errors[pnam] = True
    pnam = 'trg_binning'
    try:
        t = child02_input[pnam].get()
        n = int(t)
        if n < 1 or n > 64:
            raise ValueError('Error in {}, out of range >>> {}'.format(params[pnam],t))
        values[pnam] = n
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
            child02_err[pnam].place(x=x0,y=y); y += dy
        else:
            child02_err[pnam].place_forget(); y += dy
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
        child02_win.destroy()
    return

def run():
    sys.stderr.write('Running process 02.\n')
