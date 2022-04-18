import os
import sys
import tkinter as tk
from tkinter import ttk
import tkfilebrowser

proc_name = 'orthomosaic'
proc_title = 'Make Orthomosaic'
pnams = []
pnams.append('inpdirs')
pnams.append('outdir')
pnams.append('test1')
pnams.append('test2')
pnams.append('test3')
pnams.append('test4')
pnams.append('test5')
pnams.append('test6')
pnams.append('test7')
pnams.append('test8')
pnams.append('test9')
params = {}
params['inpdirs'] = 'Input Folders'
params['outdir'] = 'Output Folder'
params['test1'] = 'Test 1'
params['test2'] = 'Test 2'
params['test3'] = 'Test 3'
params['test4'] = 'Test 4'
params['test5'] = 'Test 5'
params['test6'] = 'Test 6'
params['test7'] = 'Test 7'
params['test8'] = 'Test 8'
params['test9'] = 'Test 9'
param_types = {}
param_types['inpdirs'] = 'string'
param_types['outdir'] = 'string'
param_types['test1'] = 'int'
param_types['test2'] = 'int'
param_types['test3'] = 'int'
param_types['test4'] = 'int'
param_types['test5'] = 'int'
param_types['test6'] = 'int'
param_types['test7'] = 'int'
param_types['test8'] = 'int'
param_types['test9'] = 'int'
defaults = {}
defaults['inpdirs'] = 'input'
defaults['outdir'] = 'output'
defaults['test1'] = '1'
defaults['test2'] = '2'
defaults['test3'] = '3'
defaults['test4'] = '4'
defaults['test5'] = '5'
defaults['test6'] = '6'
defaults['test7'] = '7'
defaults['test8'] = '8'
defaults['test9'] = '9'
values = {}
for pnam in pnams:
    values[pnam] = defaults[pnam]
input_types = {}
input_types['inpdirs'] = 'askfolders'
input_types['outdir'] = 'askfolder'
input_types['test1'] = 'box'
input_types['test2'] = 'box'
input_types['test3'] = 'box'
input_types['test4'] = 'box'
input_types['test5'] = 'box'
input_types['test6'] = 'box'
input_types['test7'] = 'box'
input_types['test8'] = 'box'
input_types['test9'] = 'box'

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

def on_mousewheel(event):
    child_cnv.yview_scroll(-1*(event.delta//20),'units')

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
    child_cnv = tk.Canvas(child_win,scrollregion=(0,0,400,1000))
    child_cnv.bind_all('<MouseWheel>',on_mousewheel)
    child_cnv.place(x=0,y=0,width=380,height=200)
    child_frm = tk.Frame(child_cnv)
    child_cnv.create_window((0,0),window=child_frm,anchor=tk.NW,width=380,height=1000)
    child_scr = tk.Scrollbar(child_win,orient=tk.VERTICAL,command=child_cnv.yview)
    child_scr.place(x=380,y=0,width=20,height=200)
    child_cnv.config(yscrollcommand=child_scr.set)
    child_bar = tk.Frame(child_win)
    child_bar.place(x=0,y=200,width=400,height=40)
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
        child_label[pnam] = ttk.Label(child_frm,text=params[pnam])
        child_label[pnam].place(x=x0,y=y); y += dy

    x0 = 160
    y0 = 15
    dy = 25
    y = y0
    child_input = {}
    child_browse = {}
    for pnam in pnams:
        if input_types[pnam] == 'box':
            child_input[pnam] = ttk.Entry(child_frm,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width); y += dy
        elif input_types[pnam] == 'askfile':
            child_input[pnam] = ttk.Entry(child_frm,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            child_browse[pnam] = tk.Button(child_frm,image=browse_img,bg='white',bd=1,command=eval('lambda:ask_file("{}")'.format(pnam)))
            child_browse[pnam].image = browse_img
            child_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        elif input_types[pnam] == 'askfiles':
            child_input[pnam] = ttk.Entry(child_frm,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            child_browse[pnam] = tk.Button(child_frm,image=browse_img,bg='white',bd=1,command=eval('lambda:ask_files("{}")'.format(pnam)))
            child_browse[pnam].image = browse_img
            child_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        elif input_types[pnam] == 'askfolder':
            child_input[pnam] = ttk.Entry(child_frm,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            child_browse[pnam] = tk.Button(child_frm,image=browse_img,bg='white',bd=1,command=eval('lambda:ask_folder("{}")'.format(pnam)))
            child_browse[pnam].image = browse_img
            child_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        elif input_types[pnam] == 'askfolders':
            child_input[pnam] = ttk.Entry(child_frm,textvariable=child_var[pnam])
            child_input[pnam].place(x=x0,y=y,width=entry_width-button_width-1)
            child_browse[pnam] = tk.Button(child_frm,image=browse_img,bg='white',bd=1,command=eval('lambda:ask_folders("{}")'.format(pnam)))
            child_browse[pnam].image = browse_img
            child_browse[pnam].place(x=x0+entry_width-button_width,y=y,width=button_width,height=button_height); y += dy
        else:
            raise ValueError('Error, unsupported input type >>> '.format(input_types[pnam]))

    child_err = {}
    for pnam in pnams:
        child_err[pnam] = ttk.Label(child_frm,text='ERROR',foreground='red')

    child_btn01 = ttk.Button(child_bar,text='Set',command=modify)
    child_btn01.place(x=30,y=5,width=100)
    child_btn02 = ttk.Button(child_bar,text='Reset',command=reset)
    child_btn02.place(x=140,y=5,width=100)
    child_btn03 = ttk.Button(child_bar,text='Cancel',command=exit)
    child_btn03.place(x=250,y=5,width=100)

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
    for pnam in pnams:
        check_values[pnam] = None
        check_errors[pnam] = True
    pnam = 'inpdirs'
    try:
        t = get(pnam)
        for item in t.split(';'):
            if not os.path.isdir(item):
                raise IOError('Error in {}, no such folder >>> {}'.format(params[pnam],item))
        check_values[pnam] = t
        check_errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        check_values[pnam] = None
        check_errors[pnam] = True
    pnam = 'outdir'
    try:
        t = get(pnam)
        if not os.path.exists(t):
            os.makedirs(t)
        if not os.path.isdir(t):
            raise IOError('Error in {}, no such folder >>> {}'.format(params[pnam],t))
        check_values[pnam] = t
        check_errors[pnam] = False
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        check_values[pnam] = None
        check_errors[pnam] = True
    for pnam in pnams[2:]:
        try:
            t = get(pnam)
            v = int(t)
            if v < 0 or v > 100:
                raise ValueError('Error in {}, out of range >>> {}'.format(params[pnam],t))
            check_values[pnam] = v
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

def reset():
    for pnam in pnams:
        child_var[pnam].set(values[pnam])
    return

def exit():
    child_win.destroy()

def run():
    sys.stderr.write('Running process {}.\n'.format(proc_name))
