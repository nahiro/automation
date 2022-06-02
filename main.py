import os
import sys
import tkinter as tk
from tkinter import ttk
import tkfilebrowser
from custom_calendar import CustomDateEntry
from config import *

def set_title(pnam):
    block = top_cmb.get()
    dstr = top_cde.get()
    field_dir = top_var['field_data'].get()
    drone_dir = top_var['drone_data'].get()
    analysis_dir = top_var['drone_analysis'].get()
    proc_orthomosaic.values['inpdirs'] = os.path.join(drone_dir,block,dstr)
    proc_orthomosaic.values['outdir'] = os.path.join(analysis_dir,block,dstr,'orthomosaic')
    if proc_orthomosaic.center_var is not None:
        pnam = 'inpdirs'
        proc_orthomosaic.center_inp[pnam].delete(1.0,tk.END)
        proc_orthomosaic.center_inp[pnam].insert(1.0,proc_orthomosaic.values[pnam])
        proc_orthomosaic.center_var[pnam].set(proc_orthomosaic.values[pnam])
        pnam = 'outdir'
        proc_orthomosaic.center_var[pnam].set(proc_orthomosaic.values[pnam])


    #print('block={}, dstr={}, field_dir={}, drone_dir={}, analysis_dir={}'.format(block,dstr,field_dir,drone_dir,analysis_dir))
    #top_err[pnam].pack(pady=(0,3),side=tk.LEFT)
    return

def ask_folder(pnam,dnam=None):
    if dnam is None:
        dnam = eval(pnam)
    path = tkfilebrowser.askopendirname(initialdir=dnam)
    if len(path) > 0:
        top_var[pnam].set(path)
    return

def run_all():
    for pnam in pnams:
        if center_var[pnam].get():
            modules[pnam].run()
    return

def set_child(pnam):
    modules[pnam].set(root)

def check_child(pnam):
    for p in pnams:
        if p != pnam:
            continue
        if center_var[pnam].get():
            check_values,check_errors = modules[pnam].check_all(source='value')
            err = False
            for error in check_errors.values():
                if hasattr(error,'__iter__'):
                    for e in error:
                        if e:
                            err = True
                            break
                else:
                    if error:
                        err = True
                if err:
                    break
            if err:
                right_lbl[pnam].pack(side=tk.LEFT)
            else:
                right_lbl[pnam].pack_forget()
        else:
            right_lbl[pnam].pack_forget()
    return

def exit():
    sys.exit()
    return

root = tk.Tk()
root.title('BLB Damage Estimation')
root.geometry('{}x{}'.format(window_width,60+40*2+30*len(pnams)))
top_frame = tk.Frame(root,width=10,height=top_frame_height,background=None)
middle_frame = tk.Frame(root,width=10,height=20,background=None)
bottom_frame = tk.Frame(root,width=10,height=40,background=None)
left_frame = tk.Frame(middle_frame,width=left_frame_width,height=10,background=None)
center_canvas = tk.Canvas(middle_frame,width=30,height=10,background=None)
right_frame = tk.Frame(middle_frame,width=right_frame_width,height=10,background=None)
top_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.TOP)
middle_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,expand=True)
bottom_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.BOTTOM)
left_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.LEFT)
center_canvas.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.LEFT,expand=True)
right_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.RIGHT)
top_frame.pack_propagate(False)
middle_frame.pack_propagate(False)
bottom_frame.pack_propagate(False)
left_frame.pack_propagate(False)
center_canvas.pack_propagate(False)
right_frame.pack_propagate(False)

top_left_frame = tk.Frame(top_frame,width=left_frame_width,height=10,background=None)
top_center_frame = tk.Frame(top_frame,width=30,height=10,background=None)
top_right_frame = tk.Frame(top_frame,width=right_frame_width,height=10,background=None)
top_left_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.LEFT)
top_center_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.LEFT,expand=True)
top_right_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.RIGHT)
top_left_frame.pack_propagate(False)
top_center_frame.pack_propagate(False)
top_right_frame.pack_propagate(False)

top_center_top_frame = tk.Frame(top_center_frame,width=30,height=10,background=None)
top_center_bottom_frame = tk.Frame(top_center_frame,width=30,height=10,background=None)
top_center_top_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.TOP,expand=True)
top_center_bottom_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.TOP,expand=True)

top_right_top_frame = tk.Frame(top_right_frame,width=30,height=10,background=None)
top_right_bottom_frame = tk.Frame(top_right_frame,width=30,height=10,background=None)
top_right_top_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.TOP,expand=True)
top_right_bottom_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.TOP)
top_right_top_frame.pack_propagate(False)

top_lbl = {}
top_btn = {}
top_err = {}
top_img = {}
top_sep = {}
top_var = {}
btn_pnam = 'set'
pnam = 'block'
top_lbl[pnam] = tk.Label(top_center_top_frame,text='Block/Date')
top_lbl[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(2,0),anchor=tk.W,side=tk.LEFT)
top_cmb = ttk.Combobox(top_center_top_frame,width=10,values=['Block-'+block for block in blocks])
top_cmb.current(0)
top_cmb.pack(ipadx=0,ipady=0,padx=(0,1),pady=(5,0),fill=tk.X,side=tk.LEFT,expand=True)
top_cde = CustomDateEntry(top_center_top_frame,width=10,date_pattern=date_format)
top_cde.pack(ipadx=0,ipady=0,padx=(0,1),pady=(5,0),fill=tk.X,side=tk.LEFT,expand=True)
top_btn[pnam] = tk.Button(top_right_top_frame,text=btn_pnam.capitalize(),width=4,command=eval('lambda:set_title("{}")'.format(pnam)))
top_btn[pnam].pack(padx=(1,0),pady=(2,0),side=tk.LEFT)
top_err[pnam] = ttk.Label(top_right_top_frame,text='ERROR',foreground='red')
top_center_bottom_cnv = {}
top_center_left_cnv = {}
top_center_right_cnv = {}
top_right_bottom_cnv = {}
browse_img = tk.PhotoImage(file=browse_image)
for pnam,title in zip(['field_data','drone_data','drone_analysis'],['Field Data','Drone Data','Drone Analysis']):
    top_center_bottom_cnv[pnam] = tk.Canvas(top_center_bottom_frame,width=10,height=25)
    top_center_bottom_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,expand=True)
    top_center_left_cnv[pnam] = tk.Canvas(top_center_bottom_cnv[pnam],width=100,height=25)
    top_center_left_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.LEFT)
    top_center_left_cnv[pnam].pack_propagate(False)
    top_center_right_cnv[pnam] = tk.Canvas(top_center_bottom_cnv[pnam],width=10,height=25)
    top_center_right_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.LEFT,expand=True)
    top_lbl[pnam] = tk.Label(top_center_left_cnv[pnam],text=title)
    top_lbl[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(3,3),anchor=tk.W,side=tk.LEFT,expand=False)
    top_sep[pnam] = ttk.Separator(top_center_left_cnv[pnam],orient='horizontal')
    top_sep[pnam].pack(ipadx=0,ipady=0,padx=(0,2),pady=0,fill=tk.X,side=tk.LEFT,expand=True)
    top_var[pnam] = tk.StringVar()
    top_var[pnam].set(os.path.join(eval(pnam),'Current'))
    top_box = tk.Entry(top_center_right_cnv[pnam],textvariable=top_var[pnam])
    top_box.pack(ipadx=0,ipady=0,padx=(0,1),pady=(3,0),anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
    top_img[pnam] = tk.Button(top_center_right_cnv[pnam],image=browse_img,width=center_btn_width,bg='white',bd=1,command=eval('lambda:ask_folder("{}")'.format(pnam)))
    top_img[pnam].image = browse_img
    top_img[pnam].pack(ipadx=0,ipady=0,padx=(0,1),pady=0,anchor=tk.W,side=tk.LEFT)
    top_right_bottom_cnv[pnam] = tk.Canvas(top_right_bottom_frame,width=10,height=25)
    top_right_bottom_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,expand=True)
    top_btn[pnam] = tk.Button(top_right_bottom_cnv[pnam],text=btn_pnam.capitalize(),width=4,command=eval('lambda:set_title("{}")'.format(pnam)))
    top_btn[pnam].pack(padx=(1,0),pady=(0,2.2),side=tk.LEFT)
    top_err[pnam] = ttk.Label(top_right_bottom_cnv[pnam],text='ERROR',foreground='red')

bottom_lbl = {}
bottom_btn = {}
pnam = 'left'
bottom_lbl[pnam] = tk.Label(bottom_frame,text='')
bottom_lbl[pnam].pack(fill=tk.X,side=tk.LEFT,expand=True)
pnam = 'run'
bottom_btn[pnam] = tk.Button(bottom_frame,text=pnam.capitalize(),width=8,command=run_all)
bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
pnam = 'exit'
bottom_btn[pnam] = tk.Button(bottom_frame,text=pnam.capitalize(),width=8,command=exit)
bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
pnam = 'right'
bottom_lbl[pnam] = tk.Label(bottom_frame,text='')
bottom_lbl[pnam].pack(fill=tk.X,side=tk.LEFT,expand=True)

bgs = [None,None]
center_var = {}
center_cnv = {}
center_chk = {}
center_sep = {}
left_cnv = {}
left_btn = {}
right_cnv = {}
right_btn = {}
right_lbl = {}
for i,pnam in enumerate(pnams):
    center_var[pnam] = tk.BooleanVar()
    center_var[pnam].set(defaults[pnam])
    center_cnv[pnam] = tk.Canvas(center_canvas,background=bgs[i%2])
    center_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(0,2),fill=tk.X,expand=True)
    center_chk[pnam] = tk.Checkbutton(center_cnv[pnam],background=bgs[i%2],variable=center_var[pnam],text=titles[pnam],command=eval('lambda:check_child("{}")'.format(pnam)))
    center_chk[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
    center_sep[pnam] = ttk.Separator(center_cnv[pnam],orient='horizontal')
    center_sep[pnam].pack(ipadx=0,ipady=0,padx=(0,2),pady=0,fill=tk.X,side=tk.LEFT,expand=True)
    left_cnv[pnam] = tk.Canvas(left_frame,width=left_frame_width,height=left_cnv_height,background=bgs[i%2])
    left_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,expand=True)
    left_btn[pnam] = ttk.Button(root,text='check_{}'.format(pnam),command=eval('lambda:check_child("{}")'.format(pnam)))
    left_btn[pnam].pack_forget() # hidden
    right_cnv[pnam] = tk.Canvas(right_frame,width=right_frame_width,height=right_cnv_height,background=bgs[i%2])
    right_cnv[pnam].pack(ipadx=0,ipady=0,padx=(0,20),pady=(0,2),expand=True)
    right_cnv[pnam].pack_propagate(False)
    right_btn[pnam] = tk.Button(right_cnv[pnam],text='Set',width=4,command=eval('lambda:set_child("{}")'.format(pnam)))
    right_btn[pnam].pack(side=tk.LEFT)
    right_lbl[pnam] = ttk.Label(right_cnv[pnam],text='ERROR',foreground='red')
    check_child(pnam)
root.mainloop()
