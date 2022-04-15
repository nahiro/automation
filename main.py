import sys
import tkinter as tk
from tkinter import ttk
from custom_calendar import CustomDateEntry
import proc_orthomosaic
import proc_geocor
import proc_indices
import proc_identify
import proc_extract
import proc_formula
import proc_apply
import proc_output

pnams = []
pnams.append('orthomosaic')
pnams.append('geocor')
pnams.append('indices')
pnams.append('identify')
pnams.append('extract')
pnams.append('formula')
pnams.append('apply')
pnams.append('output')
modules = {}
modules['orthomosaic'] = proc_orthomosaic
modules['geocor'] = proc_geocor
modules['indices'] = proc_indices
modules['identify'] = proc_identify
modules['extract'] = proc_extract
modules['formula'] = proc_formula
modules['apply'] = proc_apply
modules['output'] = proc_output
titles = {}
for pnam in pnams:
    titles[pnam] = modules[pnam].proc_title
defaults = {}
defaults['orthomosaic'] = True
defaults['geocor'] = True
defaults['indices'] = True
defaults['identify'] = False
defaults['extract'] = False
defaults['formula'] = False
defaults['apply'] = True
defaults['output'] = True

blocks = ['1A','1B','2A','2B','3A','3B','4A','4B','5','6','7A','7B',
'8A','8B','9A','9B','10A','10B','11A','11B','12','13','14A','14B','15']

entry_width = 90
button_width = 40
button_height = 21

def set_title():
    return

def run_all():
    for pnam in pnams:
        if main_var[pnam].get():
            modules[pnam].run()
    return

def set_child(pnam):
    modules[pnam].set(main_win,main_cnv)

def check_child(pnam):
    x0 = 220+40
    y0 = 15
    dy = 25
    y = y0
    for p in pnams:
        if p != pnam:
            y += dy
            continue
        if main_var[pnam].get():
            check_values,check_errors = modules[pnam].check(source='value')
            err = False
            for error in check_errors.values():
                if error:
                    err = True
            if err:
                main_err[pnam].place(x=x0,y=y); y += dy
            else:
                main_err[pnam].place_forget(); y += dy
        else:
            main_err[pnam].place_forget(); y += dy
    return

def exit():
    sys.exit()
    return

main_win = tk.Tk()
main_win.title('BLB Damage Estimation')
main_win.geometry('{}x{}'.format(290+40,100+25*len(pnams)))
main_cnv = tk.Canvas(main_win,width=290+40,height=100+25*len(pnams))
main_cnv.pack()

x0 = 30
y0 = 10
dy = 25
y = y0
main_label01 = ttk.Label(main_cnv,text='Block')
main_label01.place(x=x0,y=y)
main_label02 = ttk.Label(main_cnv,text='Date')
main_label02.place(x=x0+entry_width+1,y=y)
y += 20
main_combo01 = ttk.Combobox(main_cnv,values=['Cihea-'+block for block in blocks])
main_combo01.current(0)
main_combo01.place(x=x0,y=y,width=entry_width)
main_combo02 = CustomDateEntry(main_cnv,date_pattern='yyyy-mmm-dd')
main_combo02.place(x=x0+entry_width+1,y=y,width=entry_width)
x0 = 180+40
main_set = ttk.Button(main_cnv,text='Set',command=set_title)
main_set.place(x=x0,y=y,width=button_width,height=button_height)

main_var = {}
for pnam in pnams:
    main_var[pnam] = tk.BooleanVar()
    main_var[pnam].set(defaults[pnam])

x0 = 30
y0 = 55
y = y0
main_chk = {}
for pnam in pnams:
    main_chk[pnam] = tk.Checkbutton(main_cnv,variable=main_var[pnam],text=titles[pnam],command=eval('lambda:check_child("{}")'.format(pnam)))
    main_chk[pnam].place(x=x0,y=y); y += dy

main_hid = {}
for pnam in pnams:
    main_hid[pnam] = ttk.Button(main_cnv,text='check_{}'.format(pnam),command=eval('lambda:check_child("{}")'.format(pnam)))
    main_hid[pnam].place_forget() # hidden

x0 = 180+40
y = y0
main_btn = {}
for pnam in pnams:
    main_btn[pnam] = ttk.Button(main_cnv,text='Set',command=eval('lambda:set_child("{}")'.format(pnam)))
    main_btn[pnam].place(x=x0,y=y,width=button_width,height=button_height); y += dy
y += dy*0.2

x0 = 220+40
y = y0
main_err = {}
for pnam in pnams:
    main_err[pnam] = ttk.Label(main_cnv,text='ERROR',foreground='red')
    check_values,check_errors = modules[pnam].check(source='value')
    err = False
    for error in check_errors.values():
        if error:
            err = True
    if err and main_var[pnam].get():
        main_err[pnam].place(x=x0,y=y); y += dy
    else:
        main_err[pnam].place_forget(); y += dy
main_btn01 = ttk.Button(main_cnv,text='Run',command=run_all)
main_btn02 = ttk.Button(main_cnv,text='Exit',command=exit)
main_btn01.place(x=60+20,y=y)
main_btn02.place(x=150+20,y=y)

main_win.columnconfigure(0,weight=1)
main_win.rowconfigure(0,weight=1)
main_cnv.columnconfigure(1,weight=1)
main_win.mainloop()
