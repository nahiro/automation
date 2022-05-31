import os
import sys
import numpy as np
import tkinter as tk
from tkinter import ttk
import tkfilebrowser
from subprocess import call
from proc_func import *

HOME = os.environ.get('USERPROFILE')
if HOME is None:
    HOME = os.environ.get('HOME')

class Process:

    def __init__(self):
        self.proc_name = 'process'
        self.proc_title = 'Process Title'
        self.pnams = []
        self.params = {}
        self.param_types = {}
        self.param_range = {}
        self.defaults = {}
        self.list_sizes = {}
        self.list_labels = {}
        self.values = {}
        self.input_types = {}
        self.flag_fill = {}

        self.top_frame_height = 5
        self.bottom_frame_height = 40
        self.left_frame_width = 180
        self.right_frame_width = 70
        self.middle_left_frame_width = 700
        self.left_cnv_height = 25
        self.center_cnv_height = 25
        self.right_cnv_height = 25
        self.center_btn_width = 20
        self.inidir = os.path.join(HOME,'Work','Drone')
        if not os.path.isdir(self.inidir):
            self.inidir = os.path.join(HOME,'Documents')
        self.scrdir = os.path.join(HOME,'Script')
        self.browse_image = os.path.join(HOME,'Pictures','browse.png')
        self.root = None
        self.chk_btn = None
        self.middle_left_canvas = None
        self.middle_left_frame = None
        self.center_var = None
        self.center_cnv = None
        self.center_inp = None
        self.right_lbl = None

    def ask_file(self,pnam,dnam=None):
        if dnam is None:
            dnam = self.inidir
        path = tkfilebrowser.askopenfilename(initialdir=dnam)
        if len(path) > 0:
            self.center_var[pnam].set(path)
        return

    def ask_files(self,pnam,dnam=None):
        if dnam is None:
            dnam = self.inidir
        files = list(tkfilebrowser.askopenfilenames(initialdir=dnam))
        if len(files) > 0:
            path = ';'.join(files)
            self.center_var[pnam].set(path)
        return

    def ask_folder(self,pnam,dnam=None):
        if dnam is None:
            dnam = self.inidir
        path = tkfilebrowser.askopendirname(initialdir=dnam)
        if len(path) > 0:
            self.center_var[pnam].set(path)
        return

    def ask_folders(self,pnam,dnam=None):
        if dnam is None:
            dnam = self.inidir
        dirs = list(tkfilebrowser.askopendirnames(initialdir=dnam))
        if len(dirs) > 0:
            path = ';'.join(dirs)
            self.center_var[pnam].set(path)
        return

    def on_mousewheel(self,event):
        self.middle_left_canvas.yview_scroll(-1*(event.delta//20),'units')

    def on_frame_configure(self,event):
        self.root_width = self.root.winfo_width()
        self.center_frame_width = self.root_width-(self.left_frame_width+self.right_frame_width)
        self.middle_left_frame.config(width=self.root_width)
        for pnam in self.pnams:
            self.center_cnv[pnam].config(width=self.center_frame_width)
        return

    def reset(self):
        for pnam in self.pnams:
            if '_list' in self.param_types[pnam]:
                for j in range(self.list_sizes[pnam]):
                    if self.values[pnam][j] is not None:
                        self.center_var[pnam][j].set(self.values[pnam][j])
            else:
                if self.values[pnam] is not None:
                    self.center_var[pnam].set(self.values[pnam])
        return

    def exit(self):
        self.root.destroy()
        return

    def run(self):
        sys.stderr.write('Running process {}.\n'.format(self.proc_name))
        command = 'python'
        command += ' {}'.format(os.path.join(self.scrdir,'func.py'))
        call(command,shell=True)
        return

    def modify(self):
        check_values,check_errors = self.check_all(source='input')
        err = False
        for pnam in self.pnams:
            if '_list' in self.param_types[pnam]:
                for j in range(self.list_sizes[pnam]):
                    value = check_values[pnam][j]
                    error = check_errors[pnam][j]
                    if error:
                        err = True
                    else:
                        self.values[pnam][j] = value
            else:
                value = check_values[pnam]
                error = check_errors[pnam]
                if error:
                    err = True
                else:
                    self.values[pnam] = value
        if not err:
            self.chk_btn.invoke()
            self.root.destroy()
        return

    def get_input(self,pnam,indx=None):
        if self.param_types[pnam] == 'boolean':
            return self.center_var[pnam].get()
        elif self.param_types[pnam] == 'boolean_list':
            return self.center_var[pnam][indx].get()
        else:
            if indx is not None:
                return self.center_inp[pnam][indx].get()
            else:
                return self.center_inp[pnam].get()

    def get_value(self,pnam,indx=None):
        if indx is not None:
            return self.values[pnam][indx]
        else:
            return self.values[pnam]

    def check_par(self,pnam,t):
        if self.input_types[pnam] == 'box':
            if self.param_types[pnam] == 'string':
                return True
            elif self.param_types[pnam] == 'int':
                return check_int(self.params[pnam],t,self.param_range[pnam][0],self.param_range[pnam][1])
            elif self.param_types[pnam] == 'float':
                return check_float(self.params[pnam],t,self.param_range[pnam][0],self.param_range[pnam][1])
        elif self.input_types[pnam] == 'ask_file':
            return check_file(self.params[pnam],t)
        elif self.input_types[pnam] == 'ask_files':
            return check_files(self.params[pnam],t)
        elif self.input_types[pnam] == 'ask_folder':
            return check_folder(self.params[pnam],t)
        elif self.input_types[pnam] == 'ask_folders':
            return check_folders(self.params[pnam],t)
        elif self.input_types[pnam] == 'boolean':
            return True
        elif self.input_types[pnam] == 'boolean_list':
            return True
        elif 'int_list' in self.input_types[pnam]:
            return check_int(self.params[pnam],t,self.param_range[pnam][0],self.param_range[pnam][1])
        elif 'float_list' in self.input_types[pnam]:
            return check_float(self.params[pnam],t,self.param_range[pnam][0],self.param_range[pnam][1])
        elif '_select' in self.input_types[pnam]:
            return True
        elif '_select_list' in self.input_types[pnam]:
            return True
        else:
            raise ValueError('Error, unsupported input type ({}) >>> {}'.format(pnam,self.input_types[pnam]))

    def check_err(self,pnam,t):
        ret = self.check_par(pnam,t)
        if self.right_lbl[pnam] is not None:
            if ret:
                self.right_lbl[pnam].pack_forget()
            else:
                self.right_lbl[pnam].pack(side=tk.LEFT)
        return ret

    def check_all(self,source='input'):
        if source == 'input':
            get = self.get_input
        elif source == 'value':
            get = self.get_value
        else:
            raise ValueError('Error, source={}'.format(source))
        check_values = {}
        check_errors = {}
        for pnam in self.pnams:
            if '_list' in self.param_types[pnam]:
                check_values[pnam] = []
                check_errors[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    check_values[pnam].append(None)
                    check_errors[pnam].append(True)
                try:
                    for j in range(self.list_sizes[pnam]):
                        t = get(pnam,j)
                        ret = self.check_par(pnam,t)
                        if ret:
                            if self.center_var is None:
                                check_values[pnam][j] = self.values[pnam][j]
                            else:
                                check_values[pnam][j] = self.center_var[pnam][j].get()
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
                    ret = self.check_par(pnam,t)
                    if ret:
                        if self.center_var is None:
                            check_values[pnam] = self.values[pnam]
                        else:
                            check_values[pnam] = self.center_var[pnam].get()
                    else:
                        raise ValueError('ERROR')
                    check_errors[pnam] = False
                except Exception as e:
                    sys.stderr.write(str(e)+'\n')
        if source == 'input':
            for pnam in self.pnams:
                if not pnam in check_errors or not pnam in self.right_lbl:
                    continue

                if '_list' in self.param_types[pnam]:
                    if True in check_errors[pnam]:
                        self.right_lbl[pnam].pack(side=tk.LEFT)
                    else:
                        self.right_lbl[pnam].pack_forget()
                else:
                    if check_errors[pnam]:
                        self.right_lbl[pnam].pack(side=tk.LEFT)
                    else:
                        self.right_lbl[pnam].pack_forget()
        return check_values,check_errors

    def set(self,parent):
        if self.root is not None and self.root.winfo_exists():
            return
        for x in parent.winfo_children():
            if isinstance(x,ttk.Button) and x['text'] == 'check_{}'.format(self.proc_name):
                self.chk_btn = x
        self.root = tk.Toplevel(parent)
        self.root.title(self.proc_title)
        self.root.geometry('{}x{}'.format(self.middle_left_frame_width,self.top_frame_height+self.bottom_frame_height+len(self.pnams)*(self.center_cnv_height+2)))
        self.top_frame = tk.Frame(self.root,width=10,height=self.top_frame_height,background=None)
        self.middle_frame = tk.Frame(self.root,width=10,height=20,background=None)
        self.bottom_frame = tk.Frame(self.root,width=10,height=self.bottom_frame_height,background=None)
        self.middle_left_canvas = tk.Canvas(self.middle_frame,width=30,height=10,scrollregion=(0,0,self.middle_left_frame_width,self.top_frame_height+self.bottom_frame_height+len(self.pnams)*(self.center_cnv_height+2)),background=None)
        self.middle_left_canvas.bind_all('<MouseWheel>',self.on_mousewheel)
        self.middle_right_scr = tk.Scrollbar(self.middle_frame,orient=tk.VERTICAL,command=self.middle_left_canvas.yview)
        self.top_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.TOP)
        self.middle_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,expand=True)
        self.bottom_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.BOTTOM)
        self.middle_left_canvas.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.LEFT,expand=True)
        self.middle_right_scr.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.LEFT)
        self.top_frame.pack_propagate(False)
        self.middle_frame.pack_propagate(False)
        self.bottom_frame.pack_propagate(False)
        self.middle_left_canvas.pack_propagate(False)

        self.middle_left_frame = tk.Frame(self.middle_left_canvas,background=None)
        self.middle_left_canvas.create_window(0,0,window=self.middle_left_frame,anchor=tk.NW)
        self.middle_left_canvas.config(yscrollcommand=self.middle_right_scr.set)

        self.left_frame = tk.Frame(self.middle_left_frame,width=self.left_frame_width,height=10,background=None)
        self.left_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.LEFT)
        self.center_frame = tk.Frame(self.middle_left_frame,width=30,height=10,background=None)
        self.center_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.LEFT,expand=True)
        self.right_frame = tk.Frame(self.middle_left_frame,width=self.right_frame_width,height=10,background=None)
        self.right_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.RIGHT)
        self.middle_left_frame.pack_propagate(False)
        self.left_frame.pack_propagate(False)
        self.right_frame.pack_propagate(False)
        self.middle_left_frame.config(width=self.middle_left_frame_width,height=8000)

        self.bottom_lbl = {}
        self.bottom_btn = {}
        pnam = 'left'
        self.bottom_lbl[pnam] = tk.Label(self.bottom_frame,text='')
        self.bottom_lbl[pnam].pack(fill=tk.X,side=tk.LEFT,expand=True)
        pnam = 'set'
        self.bottom_btn[pnam] = tk.Button(self.bottom_frame,text=pnam.capitalize(),width=8,command=self.modify)
        self.bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
        pnam = 'reset'
        self.bottom_btn[pnam] = tk.Button(self.bottom_frame,text=pnam.capitalize(),width=8,command=self.reset)
        self.bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
        pnam = 'cancel'
        self.bottom_btn[pnam] = tk.Button(self.bottom_frame,text=pnam.capitalize(),width=8,command=self.exit)
        self.bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
        pnam = 'right'
        self.bottom_lbl[pnam] = tk.Label(self.bottom_frame,text='')
        self.bottom_lbl[pnam].pack(fill=tk.X,side=tk.LEFT,expand=True)

        browse_img = tk.PhotoImage(file=self.browse_image)
        bgs = [None,None]
        self.center_var = {}
        self.center_cnv = {}
        self.center_inp = {}
        self.center_lbl = {}
        self.center_btn = {}
        self.left_cnv = {}
        self.left_lbl = {}
        self.left_sep = {}
        self.right_cnv = {}
        self.right_lbl = {}
        self.center_frame.update()
        self.center_frame_width = self.root.winfo_width()-(self.left_frame_width+self.right_frame_width)
        for i,pnam in enumerate(self.pnams):
            if self.param_types[pnam] == 'string':
                self.center_var[pnam] = tk.StringVar()
            elif self.param_types[pnam] == 'int':
                self.center_var[pnam] = tk.IntVar()
            elif self.param_types[pnam] == 'float':
                self.center_var[pnam] = tk.DoubleVar()
            elif self.param_types[pnam] == 'boolean':
                self.center_var[pnam] = tk.BooleanVar()
            elif self.param_types[pnam] == 'string_select':
                self.center_var[pnam] = tk.StringVar()
            elif self.param_types[pnam] == 'int_select':
                self.center_var[pnam] = tk.IntVar()
            elif self.param_types[pnam] == 'float_select':
                self.center_var[pnam] = tk.DoubleVar()
            elif self.param_types[pnam] == 'string_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.StringVar())
            elif self.param_types[pnam] == 'int_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.IntVar())
            elif self.param_types[pnam] == 'float_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.DoubleVar())
            elif self.param_types[pnam] == 'boolean_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.BooleanVar())
            elif self.param_types[pnam] == 'string_select_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.StringVar())
            elif self.param_types[pnam] == 'int_select_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.IntVar())
            else:
                raise ValueError('Error, unsupported parameter type ({}) >>> {}'.format(pnam,self.param_types[pnam]))
            if '_list' in self.input_types[pnam]:
                for j in range(self.list_sizes[pnam]):
                    if self.values[pnam][j] is not None:
                        self.center_var[pnam][j].set(self.values[pnam][j])
            else:
                if self.values[pnam] is not None:
                    self.center_var[pnam].set(self.values[pnam])
            self.center_cnv[pnam] = tk.Canvas(self.center_frame,width=self.center_frame_width,height=self.center_cnv_height,background=bgs[i%2],highlightthickness=0)
            self.center_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(0,2))
            self.center_cnv[pnam].pack_propagate(False)
            if self.input_types[pnam] == 'box':
                self.center_inp[pnam] = tk.Entry(self.center_cnv[pnam],background=bgs[i%2],textvariable=self.center_var[pnam])
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            elif self.input_types[pnam] == 'ask_file':
                self.center_inp[pnam] = tk.Entry(self.center_cnv[pnam],background=bgs[i%2],textvariable=self.center_var[pnam])
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                self.center_btn[pnam] = tk.Button(self.center_cnv[pnam],image=browse_img,width=self.center_btn_width,bg='white',bd=1,command=eval('lambda self=self:self.ask_file("{}")'.format(pnam)))
                self.center_btn[pnam].image = browse_img
                self.center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
            elif self.input_types[pnam] == 'ask_files':
                self.center_inp[pnam] = tk.Entry(self.center_cnv[pnam],background=bgs[i%2],textvariable=self.center_var[pnam])
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                self.center_btn[pnam] = tk.Button(self.center_cnv[pnam],image=browse_img,width=self.center_btn_width,bg='white',bd=1,command=eval('lambda self=self:self.ask_files("{}")'.format(pnam)))
                self.center_btn[pnam].image = browse_img
                self.center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
            elif self.input_types[pnam] == 'ask_folder':
                self.center_inp[pnam] = tk.Entry(self.center_cnv[pnam],background=bgs[i%2],textvariable=self.center_var[pnam])
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                self.center_btn[pnam] = tk.Button(self.center_cnv[pnam],image=browse_img,width=self.center_btn_width,bg='white',bd=1,command=eval('lambda self=self:self.ask_folder("{}")'.format(pnam)))
                self.center_btn[pnam].image = browse_img
                self.center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
            elif self.input_types[pnam] == 'ask_folders':
                self.center_inp[pnam] = tk.Entry(self.center_cnv[pnam],background=bgs[i%2],textvariable=self.center_var[pnam])
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                self.center_btn[pnam] = tk.Button(self.center_cnv[pnam],image=browse_img,width=self.center_btn_width,bg='white',bd=1,command=eval('lambda self=self:self.ask_folders("{}")'.format(pnam)))
                self.center_btn[pnam].image = browse_img
                self.center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
            elif self.input_types[pnam] == 'boolean':
                self.center_inp[pnam] = tk.Checkbutton(self.center_cnv[pnam],background=bgs[i%2],variable=self.center_var[pnam])
                if pnam in self.flag_fill and self.flag_fill[pnam]:
                    self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                else:
                    self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
            elif self.input_types[pnam] == 'boolean_list':
                self.center_inp[pnam] = []
                self.center_lbl[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_inp[pnam].append(tk.Checkbutton(self.center_cnv[pnam],background=bgs[i%2],variable=self.center_var[pnam][j],text=self.list_labels[pnam][j]))
                    if pnam in self.flag_fill and self.flag_fill[pnam]:
                        self.center_inp[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                    else:
                        self.center_inp[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
            elif '_select_list' in self.input_types[pnam]:
                self.center_inp[pnam] = []
                self.center_lbl[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    if self.list_labels[pnam][j] != '':
                        self.center_lbl[pnam].append(ttk.Label(self.center_cnv[pnam],text=self.list_labels[pnam][j][0]))
                        self.center_lbl[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
                    self.center_inp[pnam].append(ttk.Combobox(self.center_cnv[pnam],width=1,background=bgs[i%2],values=self.list_labels[pnam][j][1],state='readonly',textvariable=self.center_var[pnam][j]))
                    self.center_inp[pnam][j].current(self.list_labels[pnam][j][1].index(self.values[pnam][j]))
                    self.center_inp[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            elif '_list' in self.input_types[pnam]:
                self.center_inp[pnam] = []
                self.center_lbl[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    if self.list_labels[pnam][j] != '':
                        self.center_lbl[pnam].append(ttk.Label(self.center_cnv[pnam],text=self.list_labels[pnam][j]))
                        self.center_lbl[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
                    self.center_inp[pnam].append(tk.Entry(self.center_cnv[pnam],width=1,background=bgs[i%2],textvariable=self.center_var[pnam][j]))
                    self.center_inp[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            elif '_select' in self.input_types[pnam]:
                self.center_inp[pnam] = ttk.Combobox(self.center_cnv[pnam],background=bgs[i%2],values=self.list_labels[pnam],state='readonly',textvariable=self.center_var[pnam])
                self.center_inp[pnam].current(self.list_labels[pnam].index(self.values[pnam]))
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            else:
                raise ValueError('Error, unsupported input type ({}) >>> {}'.format(pnam,self.input_types[pnam]))
            self.left_cnv[pnam] = tk.Canvas(self.left_frame,width=self.left_frame_width,height=self.left_cnv_height,background=bgs[i%2],highlightthickness=0)
            self.left_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(0,2))
            self.left_lbl[pnam] = ttk.Label(self.left_cnv[pnam],text=self.params[pnam])
            self.left_lbl[pnam].pack(ipadx=0,ipady=0,padx=(20,2),pady=0,side=tk.LEFT)
            self.left_sep[pnam] = ttk.Separator(self.left_cnv[pnam],orient='horizontal')
            self.left_sep[pnam].pack(ipadx=0,ipady=0,padx=(0,2),pady=0,fill=tk.X,side=tk.LEFT,expand=True)
            self.left_cnv[pnam].pack_propagate(False)
            self.right_cnv[pnam] = tk.Canvas(self.right_frame,width=self.right_frame_width,height=self.right_cnv_height,background=bgs[i%2],highlightthickness=0)
            self.right_cnv[pnam].pack(ipadx=0,ipady=0,padx=(0,20),pady=(0,2))
            self.right_cnv[pnam].pack_propagate(False)
            self.right_lbl[pnam] = ttk.Label(self.right_cnv[pnam],text='ERROR',foreground='red')
        for pnam in self.pnams:
            if self.param_types[pnam] == 'boolean' or self.param_types[pnam] == 'boolean_list':
                pass
            elif '_select' in self.param_types[pnam]:
                pass
            elif '_list' in self.param_types[pnam]:
                for j in range(self.list_sizes[pnam]):
                    vcmd = (self.center_inp[pnam][j].register(eval('lambda x,self=self:self.check_err("{}",x)'.format(pnam))),'%P')
                    self.center_inp[pnam][j].config(validatecommand=vcmd,validate='focusout')
            else:
                vcmd = (self.center_inp[pnam].register(eval('lambda x,self=self:self.check_err("{}",x)'.format(pnam))),'%P')
                self.center_inp[pnam].config(validatecommand=vcmd,validate='focusout')
        self.check_all(source='input')
        self.root.bind('<Configure>',self.on_frame_configure)
