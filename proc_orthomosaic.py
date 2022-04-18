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
defaults['test1'] = 1
defaults['test2'] = 2
defaults['test3'] = 3
defaults['test4'] = 4
defaults['test5'] = 5
defaults['test6'] = 6
defaults['test7'] = 7
defaults['test8'] = 8
defaults['test9'] = 9
values = {}
for pnam in pnams:
    values[pnam] = defaults[pnam]
input_types = {}
input_types['inpdirs'] = 'ask_folders'
input_types['outdir'] = 'ask_folder'
input_types['test1'] = 'box'
input_types['test2'] = 'box'
input_types['test3'] = 'box'
input_types['test4'] = 'box'
input_types['test5'] = 'box'
input_types['test6'] = 'box'
input_types['test7'] = 'box'
input_types['test8'] = 'box'
input_types['test9'] = 'box'

top_frame_height = 5
bottom_frame_height = 40
left_frame_width = 130
right_frame_width = 70
middle_left_frame_width = 400
left_cnv_height = 25
center_cnv_height = 25
right_cnv_height = 25
center_btn_width = 20
inidir = os.path.join(os.environ.get('USERPROFILE'),'Work','Drone')
if not os.path.isdir(inidir):
    inidir = os.path.join(os.environ.get('USERPROFILE'),'Documents')
browse_image = os.path.join(os.environ.get('USERPROFILE'),'Pictures','browse.png')
root = None
chk_btn = None
middle_left_canvas = None
middle_left_frame = None
center_var = None
center_cnv = None
center_inp = None
right_lbl = None

def ask_file(pnam,dnam=inidir):
    path = tkfilebrowser.askopenfilename(initialdir=dnam)
    if len(path) > 0:
        center_var[pnam].set(path)
    return

def ask_files(pnam,dnam=inidir):
    files = list(tkfilebrowser.askopenfilenames(initialdir=dnam))
    if len(files) > 0:
        path = ';'.join(files)
        center_var[pnam].set(path)
    return

def ask_folder(pnam,dnam=inidir):
    path = tkfilebrowser.askopendirname(initialdir=dnam)
    if len(path) > 0:
        center_var[pnam].set(path)
    return

def ask_folders(pnam,dnam=inidir):
    dirs = list(tkfilebrowser.askopendirnames(initialdir=dnam))
    if len(dirs) > 0:
        path = ';'.join(dirs)
        center_var[pnam].set(path)
    return

def on_mousewheel(event):
    middle_left_canvas.yview_scroll(-1*(event.delta//20),'units')

def on_frame_configure(event):
    root_width = root.winfo_width()
    center_frame_width = root_width-(left_frame_width+right_frame_width)
    middle_left_frame.config(width=root_width)
    for pnam in pnams:
        center_cnv[pnam].config(width=center_frame_width)
    return

def reset():
    for pnam in pnams:
        center_var[pnam].set(values[pnam])
    return

def exit():
    root.destroy()
    return

def run():
    sys.stderr.write('Running process {}.\n'.format(proc_name))
    return

def modify():
    global values
    check_values,check_errors = check_all(source='input')
    err = False
    for pnam in pnams:
        value = check_values[pnam]
        error = check_errors[pnam]
        if error:
            err = True
        else:
            values[pnam] = value
    if not err:
        chk_btn.invoke()
        root.destroy()
    return

def get_input(pnam):
    return center_inp[pnam].get()

def get_value(pnam):
    return values[pnam]

def check_inpdirs(t):
    pnam = 'inpdirs'
    try:
        for item in t.split(';'):
            if not os.path.isdir(item):
                raise IOError('Error in {}, no such folder >>> {}'.format(params[pnam],item))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_outdir(t):
    pnam = 'outdir'
    try:
        if not os.path.exists(t):
            os.makedirs(t)
        if not os.path.isdir(t):
            raise IOError('Error in {}, no such folder >>> {}'.format(params[pnam],item))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_int(pnam,t):
    try:
        v = int(t)
        if v < 0 or v > 100:
            raise ValueError('Error in {}, out of range >>> {}'.format(params[pnam],t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_err(pnam,t):
    if pnam in pnams[2:]:
        ret = eval('check_int("{}",t)'.format(pnam))
    else:
        ret = eval('check_{}(t)'.format(pnam))
    if right_lbl[pnam] is not None:
        if ret:
            right_lbl[pnam].pack_forget()
        else:
            right_lbl[pnam].pack(side=tk.LEFT)
    return ret

def check_all(source='input'):
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
    for pnam in pnams:
        try:
            t = get(pnam)
            if pnam in pnams[2:]:
                ret = eval('check_int("{}",t)'.format(pnam))
            else:
                ret = eval('check_{}(t)'.format(pnam))
            if ret:
                if center_var is None:
                    check_values[pnam] = values[pnam]
                else:
                    check_values[pnam] = center_var[pnam].get()
                check_errors[pnam] = False
            else:
                raise ValueError('ERROR')
        except Exception as e:
            sys.stderr.write(str(e)+'\n')
    if source == 'input':
        for pnam in pnams:
            if not pnam in check_errors or not pnam in right_lbl:
                continue
            if check_errors[pnam]:
                right_lbl[pnam].pack(side=tk.LEFT)
            else:
                right_lbl[pnam].pack_forget()
    return check_values,check_errors

def set(parent):
    global root
    global chk_btn
    global middle_left_canvas
    global middle_left_frame
    global center_var
    global center_cnv
    global center_inp
    global right_lbl

    if root is not None and root.winfo_exists():
        return
    for x in parent.winfo_children():
        if isinstance(x,ttk.Button) and x['text'] == 'check_{}'.format(proc_name):
            chk_btn = x
    root = tk.Toplevel(parent)
    root.title(proc_title)
    root.geometry('400x200')
    top_frame = tk.Frame(root,width=10,height=top_frame_height,background=None)
    middle_frame = tk.Frame(root,width=10,height=20,background=None)
    bottom_frame = tk.Frame(root,width=10,height=bottom_frame_height,background=None)
    middle_left_canvas = tk.Canvas(middle_frame,width=30,height=10,scrollregion=(0,0,400,top_frame_height+bottom_frame_height+len(params)*(center_cnv_height+2)),background=None)
    middle_left_canvas.bind_all('<MouseWheel>',on_mousewheel)
    middle_right_scr = tk.Scrollbar(middle_frame,orient=tk.VERTICAL,command=middle_left_canvas.yview)
    top_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.TOP)
    middle_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,expand=True)
    bottom_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.BOTTOM)
    middle_left_canvas.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.LEFT,expand=True)
    middle_right_scr.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.LEFT)
    top_frame.pack_propagate(False)
    middle_frame.pack_propagate(False)
    bottom_frame.pack_propagate(False)
    middle_left_canvas.pack_propagate(False)

    middle_left_frame = tk.Frame(middle_left_canvas,background=None)
    middle_left_canvas.create_window(0,0,window=middle_left_frame,anchor=tk.NW)
    middle_left_canvas.config(yscrollcommand=middle_right_scr.set)

    left_frame = tk.Frame(middle_left_frame,width=left_frame_width,height=10,background=None)
    left_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.LEFT)
    center_frame = tk.Frame(middle_left_frame,width=30,height=10,background=None)
    center_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.LEFT,expand=True)
    right_frame = tk.Frame(middle_left_frame,width=right_frame_width,height=10,background=None)
    right_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.RIGHT)
    middle_left_frame.pack_propagate(False)
    left_frame.pack_propagate(False)
    right_frame.pack_propagate(False)
    middle_left_frame.config(width=middle_left_frame_width,height=8000)

    bottom_lbl = {}
    bottom_btn = {}
    pnam = 'left'
    bottom_lbl[pnam] = tk.Label(bottom_frame,text='')
    bottom_lbl[pnam].pack(fill=tk.X,side=tk.LEFT,expand=True)
    pnam = 'set'
    bottom_btn[pnam] = tk.Button(bottom_frame,text=pnam.capitalize(),width=8,command=modify)
    bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
    pnam = 'reset'
    bottom_btn[pnam] = tk.Button(bottom_frame,text=pnam.capitalize(),width=8,command=reset)
    bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
    pnam = 'cancel'
    bottom_btn[pnam] = tk.Button(bottom_frame,text=pnam.capitalize(),width=8,command=exit)
    bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
    pnam = 'right'
    bottom_lbl[pnam] = tk.Label(bottom_frame,text='')
    bottom_lbl[pnam].pack(fill=tk.X,side=tk.LEFT,expand=True)

    browse_img = tk.PhotoImage(file=browse_image)
    bgs = [None,None]
    #bgs = ['#aaaaaa','#cccccc']
    center_var = {}
    center_cnv = {}
    center_inp = {}
    center_btn = {}
    center_left_frame = {}
    center_right_frame = {}
    left_cnv = {}
    left_lbl = {}
    left_sep = {}
    right_cnv = {}
    right_lbl = {}
    center_frame.update()
    center_frame_width = root.winfo_width()-(left_frame_width+right_frame_width)
    for i,pnam in enumerate(pnams):
        if param_types[pnam] == 'string':
            center_var[pnam] = tk.StringVar()
        elif param_types[pnam] == 'int':
            center_var[pnam] = tk.IntVar()
        elif param_types[pnam] == 'double':
            center_var[pnam] = tk.DoubleVar()
        elif param_types[pnam] == 'boolean':
            center_var[pnam] = tk.BooleanVar()
        else:
            raise ValueError('Error, unsupported parameter type ({}) >>> {}'.format(pnam,param_types[pnam]))
        center_var[pnam].set(values[pnam])
        center_cnv[pnam] = tk.Canvas(center_frame,width=center_frame_width,height=center_cnv_height,background=bgs[i%2],highlightthickness=0)
        center_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(0,2))
        center_cnv[pnam].pack_propagate(False)
        if input_types[pnam] == 'box':
            center_inp[pnam] = tk.Entry(center_cnv[pnam],background=bgs[i%2],textvariable=center_var[pnam])
            center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
        elif input_types[pnam] == 'ask_file':
            center_inp[pnam] = tk.Entry(center_cnv[pnam],background=bgs[i%2],textvariable=center_var[pnam])
            center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            center_btn[pnam] = tk.Button(center_cnv[pnam],image=browse_img,width=center_btn_width,bg='white',bd=1,command=eval('lambda:ask_file("{}")'.format(pnam)))
            center_btn[pnam].image = browse_img
            center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
        elif input_types[pnam] == 'ask_files':
            center_inp[pnam] = tk.Entry(center_cnv[pnam],background=bgs[i%2],textvariable=center_var[pnam])
            center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            center_btn[pnam] = tk.Button(center_cnv[pnam],image=browse_img,width=center_btn_width,bg='white',bd=1,command=eval('lambda:ask_files("{}")'.format(pnam)))
            center_btn[pnam].image = browse_img
            center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
        elif input_types[pnam] == 'ask_folder':
            center_inp[pnam] = tk.Entry(center_cnv[pnam],background=bgs[i%2],textvariable=center_var[pnam])
            center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            center_btn[pnam] = tk.Button(center_cnv[pnam],image=browse_img,width=center_btn_width,bg='white',bd=1,command=eval('lambda:ask_folder("{}")'.format(pnam)))
            center_btn[pnam].image = browse_img
            center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
        elif input_types[pnam] == 'ask_folders':
            center_inp[pnam] = tk.Entry(center_cnv[pnam],background=bgs[i%2],textvariable=center_var[pnam])
            center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            center_btn[pnam] = tk.Button(center_cnv[pnam],image=browse_img,width=center_btn_width,bg='white',bd=1,command=eval('lambda:ask_folders("{}")'.format(pnam)))
            center_btn[pnam].image = browse_img
            center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
        else:
            raise ValueError('Error, unsupported input type ({}) >>> {}'.format(pnam,input_types[pnam]))
        left_cnv[pnam] = tk.Canvas(left_frame,width=left_frame_width,height=left_cnv_height,background=bgs[i%2])
        left_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(0,2))
        left_lbl[pnam] = ttk.Label(left_cnv[pnam],text=params[pnam])
        left_lbl[pnam].pack(ipadx=0,ipady=0,padx=(20,2),pady=0,side=tk.LEFT)
        left_sep[pnam] = ttk.Separator(left_cnv[pnam],orient='horizontal')
        left_sep[pnam].pack(ipadx=0,ipady=0,padx=(0,2),pady=0,fill=tk.X,side=tk.LEFT,expand=True)
        left_cnv[pnam].pack_propagate(False)
        right_cnv[pnam] = tk.Canvas(right_frame,width=right_frame_width,height=right_cnv_height,background=bgs[i%2])
        right_cnv[pnam].pack(ipadx=0,ipady=0,padx=(0,20),pady=(0,2))
        right_cnv[pnam].pack_propagate(False)
        right_lbl[pnam] = ttk.Label(right_cnv[pnam],text='ERROR',foreground='red')
    for pnam in pnams:
        vcmd = (center_inp[pnam].register(eval('lambda x:check_err("{}",x)'.format(pnam))),'%P')
        center_inp[pnam].config(validatecommand=vcmd,validate='focusout')
    check_all(source='input')
    root.bind('<Configure>',on_frame_configure)
