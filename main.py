import sys
import tkinter
from tkinter import ttk
import proc_orthomosaic
import proc_geocor
import proc_indices
import proc_points
import proc_formula
import proc_apply
import proc_output

pnams = []
pnams.append('orthomosaic')
pnams.append('geocor')
pnams.append('indices')
pnams.append('points')
pnams.append('formula')
pnams.append('apply')
pnams.append('output')
procs = {}
procs['orthomosaic'] = 'Make Orthomosaic'
procs['geocor'] = 'Geometric Correction'
procs['indices'] = 'Calculate Indices'
procs['points'] = 'Extract Points'
procs['formula'] = 'Make Formula'
procs['apply'] = 'Apply Formula'
procs['output'] = 'Output Results'
defaults = {}
defaults['orthomosaic'] = True
defaults['geocor'] = True
defaults['indices'] = True
defaults['points'] = False
defaults['formula'] = False
defaults['apply'] = True
defaults['output'] = True
modules = {}
modules['orthomosaic'] = proc_orthomosaic
modules['geocor'] = proc_geocor
modules['indices'] = proc_indices
modules['points'] = proc_points
modules['formula'] = proc_formula
modules['apply'] = proc_apply
modules['output'] = proc_output

button_width = 40
button_height = 21

def run_all():
    for pnam in pnams:
        if main_var[pnam].get():
            modules[pnam].run()
    return

def set_child(pnam):
    modules[pnam].set(main_win,main_frm)

def check_child(pnam):
    x0 = 220
    y0 = 15
    dy = 25
    y = y0
    for p in pnams:
        if p != pnam:
            y += dy
            continue
        check_values,check_errors = modules[pnam].check(source='value')
        err = False
        for error in check_errors.values():
            if error:
                err = True
        if err and main_var[pnam].get():
            main_err[pnam].place(x=x0,y=y); y += dy
        else:
            main_err[pnam].place_forget(); y += dy
    return

def exit():
    sys.exit()
    return

main_win = tkinter.Tk()
main_win.title('BLB Damage Estimation')
main_win.geometry('300x240')
main_frm = ttk.Frame(main_win)
main_frm.grid(column=0,row=0,sticky=tkinter.NSEW,padx=5,pady=10)

main_label01 = ttk.Label(main_frm,text='Process Item')
main_label01.place(x=50,y=0)

main_var = {}
for pnam in pnams:
    main_var[pnam] = tkinter.BooleanVar()
    main_var[pnam].set(defaults[pnam])

x0 = 30
y0 = 15
dy = 25
y = y0
main_chk = {}
for pnam in pnams:
    main_chk[pnam] = tkinter.Checkbutton(main_frm,variable=main_var[pnam],text=procs[pnam],command=eval('lambda:check_child("{}")'.format(pnam)))
    main_chk[pnam].place(x=x0,y=y); y += dy

main_hid = {}
for pnam in pnams:
    main_hid[pnam] = ttk.Button(main_frm,text='check_{}'.format(pnam),command=eval('lambda:check_child("{}")'.format(pnam)))
    main_hid[pnam].place_forget() # hidden

x0 = 180
y0 = 15
dy = 25
y = y0
main_btn = {}
for pnam in pnams:
    main_btn[pnam] = ttk.Button(main_frm,text='Set',command=eval('lambda:set_child("{}")'.format(pnam)))
    main_btn[pnam].place(x=x0,y=y,width=button_width,height=button_height); y += dy
y += dy*0.2

x0 = 220
y0 = 15
dy = 25
y = y0
main_err = {}
for pnam in pnams:
    main_err[pnam] = ttk.Label(main_frm,text='ERROR',foreground='red')
    check_values,check_errors = modules[pnam].check(source='value')
    err = False
    for error in check_errors.values():
        if error:
            err = True
    if err and main_var[pnam].get():
        main_err[pnam].place(x=x0,y=y); y += dy
    else:
        main_err[pnam].place_forget(); y += dy
main_btn01 = ttk.Button(main_frm,text='Run',command=run_all)
main_btn02 = ttk.Button(main_frm,text='Exit',command=exit)
main_btn01.place(x=60,y=y)
main_btn02.place(x=150,y=y)

main_win.columnconfigure(0,weight=1)
main_win.rowconfigure(0,weight=1)
main_frm.columnconfigure(1,weight=1)
main_win.mainloop()
