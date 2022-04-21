import os
import sys
import tkinter as tk
from tkinter import ttk
import tkfilebrowser
from subprocess import call

proc_name = 'geocor'
proc_title = 'Geometric Correction'
pnams = []
pnams.append('ref_fnam')
pnams.append('trg_fnam')
pnams.append('ref_pixel')
pnams.append('trg_binning')
pnams.append('part_sizes')
#pnams.append('higher_flags')
params = {}
params['ref_fnam'] = 'Reference Image'
params['trg_fnam'] = 'Orthomosaic Image'
params['ref_pixel'] = 'Reference Pixel Size'
params['trg_binning'] = 'Target Binning Number'
params['part_sizes'] = 'Partial Image Size'
params['higher_flags'] = 'Higher Order Flag'
param_types = {}
param_types['ref_fnam'] = 'string'
param_types['trg_fnam'] = 'string'
param_types['ref_pixel'] = 'double'
param_types['trg_binning'] = 'int'
param_types['part_sizes'] = 'int_list'
param_types['higher_flags'] = 'boolean_list'
defaults = {}
defaults['ref_fnam'] = 'wv2_180629_pan.tif'
defaults['trg_fnam'] = 'test.tif'
defaults['ref_pixel'] = 0.2
defaults['trg_binning'] = 8
defaults['part_sizes'] = [250,250,120,120,80]
defaults['higher_flags'] = [True,True,True]
defaults['boundary_width'] = 0.6
list_sizes = {}
list_sizes['part_sizes'] = 5
list_sizes['higher_flags'] = 3
list_labels = {}
list_labels['part_sizes'] = ['1','2','3','4','5']
list_labels['higher_flags'] = ['1st','2nd','3rd']
values = {}
for pnam in pnams:
    values[pnam] = defaults[pnam]
input_types = {}
input_types['ref_fnam'] = 'ask_file'
input_types['trg_fnam'] = 'ask_file'
input_types['ref_pixel'] = 'box'
input_types['trg_binning'] = 'box'
input_types['part_sizes'] = 'int_list'
input_types['higher_flags'] = 'boolean_list'

top_frame_height = 5
bottom_frame_height = 40
left_frame_width = 180
right_frame_width = 70
middle_left_frame_width = 450
left_cnv_height = 25
center_cnv_height = 25
right_cnv_height = 25
center_btn_width = 20
inidir = os.path.join(os.environ.get('USERPROFILE'),'Work','Drone')
if not os.path.isdir(inidir):
    inidir = os.path.join(os.environ.get('USERPROFILE'),'Documents')
scrdir = os.path.join(os.environ.get('USERPROFILE'),'Script')
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
        if '_list' in param_types[pnam]:
            for j in range(list_sizes[pnam]):
                center_var[pnam][j].set(values[pnam][j])
        else:
            center_var[pnam].set(values[pnam])
    return

def exit():
    root.destroy()
    return

def run():
    sys.stderr.write('Running process {}.\n'.format(proc_name))
    command = 'python'
    command += ' {}'.format(os.path.join(scrdir,'func.py'))
    call(command,shell=True)
    return

def modify():
    global values
    check_values,check_errors = check_all(source='input')
    err = False
    for pnam in pnams:
        if '_list' in param_types[pnam]:
            for j in range(list_sizes[pnam]):
                value = check_values[pnam][j]
                error = check_errors[pnam][j]
                if error:
                    err = True
                else:
                    values[pnam][j] = value
        else:
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

def get_input(pnam,indx=None):
    if indx is not None:
        return center_inp[pnam][indx].get()
    else:
        return center_inp[pnam].get()

def get_value(pnam,indx=None):
    if indx is not None:
        return values[pnam][indx]
    else:
        return values[pnam]

def check_ref_fnam(t):
    pnam = 'ref_fnam'
    try:
        if not os.path.exists(t):
            raise IOError('Error in {}, no such file >>> {}'.format(params[pnam],t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_trg_fnam(t):
    pnam = 'trg_fnam'
    try:
        if not os.path.exists(t):
            raise IOError('Error in {}, no such file >>> {}'.format(params[pnam],t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_ref_pixel(t):
    pnam = 'ref_pixel'
    try:
        v = float(t)
        if v < 0.01 or v > 50.0:
            raise ValueError('Error in {}, out of range >>> {}'.format(params[pnam],t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_trg_binning(t):
    pnam = 'trg_binning'
    try:
        n = int(t)
        if n < 1 or n > 64:
            raise ValueError('Error in {}, out of range >>> {}'.format(params[pnam],t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_part_sizes(t):
    pnam = 'part_sizes'
    try:
        n = int(t)
        if n < 10 or n > 1000000:
            raise ValueError('Error in {}, out of range >>> {}'.format(params[pnam],t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_err(pnam,t):
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
        if '_list' in param_types[pnam]:
            check_values[pnam] = []
            check_errors[pnam] = []
            for j in range(list_sizes[pnam]):
                check_values[pnam].append(None)
                check_errors[pnam].append(True)
            try:
                for j in range(list_sizes[pnam]):
                    t = get(pnam,j)
                    ret = eval('check_{}(t)'.format(pnam))
                    if ret:
                        if center_var is None:
                            check_values[pnam][j] = values[pnam][j]
                        else:
                            check_values[pnam][j] = center_var[pnam][j].get()
                    else:
                        raise ValueError('ERROR')
                    check_errors[pnam][j] = False
            except Exception as e:
                sys.stderr.write(str(e)+'\n')
        else:
            check_values[pnam] = None
            check_errors[pnam] = True
            try:
                t = get(pnam)
                ret = eval('check_{}(t)'.format(pnam))
                if ret:
                    if center_var is None:
                        check_values[pnam] = values[pnam]
                    else:
                        check_values[pnam] = center_var[pnam].get()
                else:
                    raise ValueError('ERROR')
                check_errors[pnam] = False
            except Exception as e:
                sys.stderr.write(str(e)+'\n')
    if source == 'input':
        for pnam in pnams:
            if not pnam in check_errors or not pnam in right_lbl:
                continue

            if '_list' in param_types[pnam]:
                if True in check_errors[pnam]:
                    right_lbl[pnam].pack(side=tk.LEFT)
                else:
                    right_lbl[pnam].pack_forget()
            else:
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
    root.geometry('{}x200'.format(middle_left_frame_width))
    top_frame = tk.Frame(root,width=10,height=top_frame_height,background=None)
    middle_frame = tk.Frame(root,width=10,height=20,background=None)
    bottom_frame = tk.Frame(root,width=10,height=bottom_frame_height,background=None)
    middle_left_canvas = tk.Canvas(middle_frame,width=30,height=10,scrollregion=(0,0,middle_left_frame_width,top_frame_height+bottom_frame_height+len(params)*(center_cnv_height+2)),background=None)
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
        elif param_types[pnam] == 'string_list':
            center_var[pnam] = []
            for j in range(list_sizes[pnam]):
                center_var[pnam].append(tk.StringVar())
        elif param_types[pnam] == 'int_list':
            center_var[pnam] = []
            for j in range(list_sizes[pnam]):
                center_var[pnam].append(tk.IntVar())
        elif param_types[pnam] == 'double_list':
            center_var[pnam] = []
            for j in range(list_sizes[pnam]):
                center_var[pnam].append(tk.DoubleVar())
        elif param_types[pnam] == 'boolean_list':
            center_var[pnam] = []
            for j in range(list_sizes[pnam]):
                center_var[pnam].append(tk.BooleanVar())
        else:
            raise ValueError('Error, unsupported parameter type ({}) >>> {}'.format(pnam,param_types[pnam]))
        if '_list' in input_types[pnam]:
            for j in range(list_sizes[pnam]):
                center_var[pnam][j].set(values[pnam][j])
        else:
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
        elif '_list' in input_types[pnam]:
            center_inp[pnam] = []
            for j in range(list_sizes[pnam]):
                center_inp[pnam].append(tk.Entry(center_cnv[pnam],width=10,background=bgs[i%2],textvariable=center_var[pnam][j]))
                center_inp[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT,expand=True)
        else:
            raise ValueError('Error, unsupported input type ({}) >>> {}'.format(pnam,input_types[pnam]))
        left_cnv[pnam] = tk.Canvas(left_frame,width=left_frame_width,height=left_cnv_height,background=bgs[i%2],highlightthickness=0)
        left_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(0,2))
        left_lbl[pnam] = ttk.Label(left_cnv[pnam],text=params[pnam])
        left_lbl[pnam].pack(ipadx=0,ipady=0,padx=(20,2),pady=0,side=tk.LEFT)
        left_sep[pnam] = ttk.Separator(left_cnv[pnam],orient='horizontal')
        left_sep[pnam].pack(ipadx=0,ipady=0,padx=(0,2),pady=0,fill=tk.X,side=tk.LEFT,expand=True)
        left_cnv[pnam].pack_propagate(False)
        right_cnv[pnam] = tk.Canvas(right_frame,width=right_frame_width,height=right_cnv_height,background=bgs[i%2],highlightthickness=0)
        right_cnv[pnam].pack(ipadx=0,ipady=0,padx=(0,20),pady=(0,2))
        right_cnv[pnam].pack_propagate(False)
        right_lbl[pnam] = ttk.Label(right_cnv[pnam],text='ERROR',foreground='red')
    for pnam in pnams:
        if '_list' in param_types[pnam]:
            for j in range(list_sizes[pnam]):
                vcmd = (center_inp[pnam][j].register(eval('lambda x:check_err("{}",x)'.format(pnam))),'%P')
                center_inp[pnam][j].config(validatecommand=vcmd,validate='focusout')
        else:
            vcmd = (center_inp[pnam].register(eval('lambda x:check_err("{}",x)'.format(pnam))),'%P')
            center_inp[pnam].config(validatecommand=vcmd,validate='focusout')
    check_all(source='input')
    root.bind('<Configure>',on_frame_configure)
