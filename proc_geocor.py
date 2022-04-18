import os
import sys
import tkinter as tk
from tkinter import ttk
import tkfilebrowser

proc_name = 'geocor'
proc_title = 'Geometric Correction'
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
input_types['ref_fnam'] = 'askfile'
input_types['trg_fnam'] = 'askfile'
input_types['ref_pixel'] = 'box'
input_types['trg_binning'] = 'box'

entry_width = 160
button_width = 20
button_height = 21
inidir = os.path.join(os.environ.get('USERPROFILE'),'Work','Drone')
browse_image = os.path.join(os.environ.get('USERPROFILE'),'Pictures','browse.png')

child_win = None
child_cnv = None
main_win = None
main_hid = None

def ask_file(pnam,dnam=inidir):
    path = tkfilebrowser.askopenfilename(initialdir=dnam)
    if len(path) > 0:
        child_var[pnam].set(path)
        defaults[pnam] = path
    return

def ask_files(pnam,dnam=inidir):
    files = list(tkfilebrowser.askopenfilenames(initialdir=dnam))
    if len(files) > 0:
        path = ';'.join(files)
        child_var[pnam].set(path)
        defaults[pnam] = path
    return

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

def set(parent):
    global main_win
    global main_hid
    global child_win
    global child_cnv
    global child_var
    global child_label
    global child_input
    global child_browse
    global child_err

    if child_win is not None and child_win.winfo_exists():
        return
    main_win = parent
    for x in main_win.winfo_children():
        if isinstance(x,ttk.Button) and x['text'] == 'check_{}'.format(proc_name):
            main_hid = x
    child_win = tk.Toplevel(parent)
    child_win.title(proc_title)
    child_win.geometry('400x240')
    child_cnv = tk.Canvas(child_win,width=400,height=240)
    child_cnv.pack()
    browse_img = tk.PhotoImage(file=browse_image)

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
        child_label[pnam] = ttk.Label(child_cnv,text=params[pnam])
        child_label[pnam].place(x=x0,y=y); y += dy

    x0 = 160
    y0 = 15
    dy = 25
    y = y0
    child_input = {}
    child_browse = {}
    for pnam in pnams:
        if input_types[pnam] == 'box':
            child_input[pnam] = ttk.Entry(child_cnv,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width); y += dy
        elif input_types[pnam] == 'askfile':
            child_input[pnam] = ttk.Entry(child_cnv,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            child_browse[pnam] = tk.Button(child_cnv,image=browse_img,bg='white',bd=1,command=eval('lambda:ask_file("{}")'.format(pnam)))
            child_browse[pnam].image = browse_img
            child_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        elif input_types[pnam] == 'askfiles':
            child_input[pnam] = ttk.Entry(child_cnv,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            child_browse[pnam] = tk.Button(child_cnv,image=browse_img,bg='white',bd=1,command=eval('lambda:ask_files("{}")'.format(pnam)))
            child_browse[pnam].image = browse_img
            child_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        elif input_types[pnam] == 'askfolder':
            child_input[pnam] = ttk.Entry(child_cnv,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            child_browse[pnam] = tk.Button(child_cnv,image=browse_img,bg='white',bd=1,command=eval('lambda:ask_folder("{}")'.format(pnam)))
            child_browse[pnam].image = browse_img
            child_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        elif input_types[pnam] == 'askfolders':
            child_input[pnam] = ttk.Entry(child_cnv,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            child_browse[pnam] = tk.Button(child_cnv,image=browse_img,bg='white',bd=1,command=eval('lambda:ask_folders("{}")'.format(pnam)))
            child_browse[pnam].image = browse_img
            child_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        else:
            raise ValueError('Error, unsupported input type >>> '.format(input_types[pnam]))

    child_err = {}
    for pnam in pnams:
        child_err[pnam] = ttk.Label(child_cnv,text='ERROR',foreground='red')

    child_btn02 = ttk.Button(child_cnv,text='Set',command=modify)
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
        main_hid.invoke()
        child_win.destroy()
    return

def run():
    sys.stderr.write('Running process {}.\n'.format(proc_name))
