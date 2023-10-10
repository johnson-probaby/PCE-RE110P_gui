import modbus_methods as mm
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter.ttk import Style
import time
import sys
import threading
from threading import Thread, Event
import re




##these are methods called when buttons are pressed
##they all access methods within modbus_methods.py 
##and retreive variables from the gui when applicable
#initiate connection
def init_con():
    global con, dc, connect_button
    global com_combobox
    cport = com_combobox.get()
    success = mm.connect_TCP(cport)
    if success: 
        print("connected")
        #connect_button.config(style = "con")
        time.sleep(0.5)
        start_periodic_read()

    else: 
        print("connection failed")
        #connect_button.config(style="dc")

#write new setpoint
def write_sv():
    global sv_entry, read
    read = False
    time.sleep(0.05)
    #print("stop reading")
    try:
        set_float = float(sv_entry.get())
    except ValueError:
        print("unallowed set value - NaN")
        read = True
        start_periodic_read()
        return

    set_int = int(set_float*10)

    if set_int>9000:
        print("unallowed set value - too high")
        read = True
        start_periodic_read()
        return
    elif set_int<0:
        print("unallowed set value - too low")
        read = True
        start_periodic_read()
        return
    else:
        mm.update_sv(set_int)
        read = True
        start_periodic_read()

#read registers
def periodic_read():
    global read, gsv, gpv1, gpv2, dT
    while read:
        try:
            mm.update_regs()

        except AttributeError:
            print("\nerror reading register - restarting\n")
        #mm.print_regs() #troubleshooting
        gsv.set(mm.sv)
        gpv1.set(mm.pv1)
        gpv2.set(mm.pv2)
        dtstr = (mm.pv1 - mm.sv)
        dts = round(dtstr,1)
        #print(dts)
        dT.set(dts)

        time.sleep(0.1)
        
def up_readout(var, ind, mode):
    dis_sv['text'] = gsv.get()
    dis_pv1['text'] = gpv1.get()
    dis_pv2['text'] = gpv2.get()
    dis_deltaT['text'] = gpv1.get() - gsv.get()

#threading for continuous register reading
def start_periodic_read():
    event = Event()
    read_thread = threading.Thread(target=periodic_read)
    read_thread.daemon = True
    read_thread.start()

##this is the beginning of the GUI interface
##currently using tkinter .grid() for organization
root = tk.Tk()
root.title("PCE Heater GUI")
LFont = tkFont.Font(size=24)

read = True
gsv = tk.DoubleVar(root, -10)
gpv1 = tk.DoubleVar(root, -10)
gpv2 = tk.DoubleVar(root, -10)
dT = tk.DoubleVar(root, -10)

gsv.trace('w',up_readout)
gpv1.trace('w',up_readout)
gpv2.trace('w',up_readout)
dT.trace('w',up_readout)

#label for com combobox
com_label = ttk.Label(root, text="IP:")
com_label.grid(row=0,column=0,padx=10,pady=5, sticky = 'e')

#find list of serial ports
comlist = mm.serial_ports()

#choose COM port/ com combobox
com_var = tk.StringVar()
text_var = com_var
com_combobox = ttk.Entry(root)
com_combobox.grid(row=0,column=1,padx=10,pady=5)
#com_combobox.set(comlist[0])

#connect button
connect_button = ttk.Button(root, text="Connect", command=init_con)
connect_button.grid(row=0, column=2, padx=10, pady=5, sticky = "w")

#connect buttion styles
con = Style()
con.configure('con',bg = 'green')
dc = Style()
dc.configure('dc', bg = 'red')

#choose set value
set_value = ttk.Label(root,text="New Set Value (°C):")
set_value.grid(row=1, column=0, padx=10, pady=5, sticky = 'e')
sv_entry = ttk.Entry(root)
sv_entry.insert(0,"0")
sv_entry.grid(row=1, column=1, padx=10, pady=5)

#write SV button
write_button = ttk.Button(root, text="Write", command=write_sv)
write_button.grid(row=1, column=2, padx=10, pady=5, sticky = "w")

#line separating 

#display register values
#this is for SV
dis_sv_label = ttk.Label(root, text = "Current Set Value (°C):", font = LFont)
dis_sv = ttk.Label(root,text =gsv.get(), font = LFont)
dis_sv_label.grid(row=3, column=0, padx=10, pady=5,rowspan=2, columnspan=3,sticky='e')
dis_sv.grid(row=3, column=3, padx=10, pady=5,rowspan=2)

#this is for PV1
dis_pv1_label = ttk.Label(root, text = "PV1 (°C):",font = LFont)
dis_pv1 = tk.Label(root,text =gpv1.get(),font = LFont)
dis_pv1_label.grid(row=5, column=0, padx=10, pady=5, rowspan=2, columnspan=3,sticky='e')
dis_pv1.grid(row=5, column=3, padx=10, pady=5, rowspan=2)

#this is for PV2
dis_pv2_label = ttk.Label(root, text = "PV2 (°C):",font = LFont)
dis_pv2 = ttk.Label(root,text =gpv2.get(),font = LFont)
dis_pv2_label.grid(row=5, column=4, padx=1, pady=5, rowspan=2, columnspan=2, sticky='e')
dis_pv2.grid(row=5, column=6, padx=10, pady=5, rowspan=2)

#this calculates delta T and displays it
dis_deltaT_label = ttk.Label(root, text = "PV1-SV1 ΔT (°C):",font = LFont)
dis_deltaT = ttk.Label(root,text = dT.get(),font = LFont)
dis_deltaT_label.grid(row=3, column=4, padx=10, pady=5, rowspan=2, columnspan=2,sticky='e')
dis_deltaT.grid(row=3, column=6, padx=10, pady=5, rowspan=2)



root.mainloop()