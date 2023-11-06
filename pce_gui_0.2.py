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
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque



##these are methods called when buttons are pressed
##they all access methods within modbus_methods.py 
##and retreive variables from the gui when applicable
#initiate connection
def init_con():
    global con, dc, connect_button
    global com_combobox
    cport = com_combobox.get()
    br = br_combo.get()
    ip = ip_entry.get()
    port = port_entry.get()
    if cselect.get()==1:
        print(f"attempting TCP connection w/ IP: {ip} port: {port} at Baud Rate: {br}...")
        success = mm.connect_TCP(ip,port, br)
        if success: 
            print("connected")
            connect_button.config(style = "con")
            time.sleep(0.3)
            start_periodic_read()
            

        else: 
            print("connection failed")
            connect_button.config(style="dc")

    else:
        print(f"attempting Serial connection w/ {cport} at Baud Rate: {br}...")
        success = mm.connect_port(cport, br)
        if success: 
            print("connected")
            #connect_button.config(style = "con")
            time.sleep(0.5)
            start_periodic_read()

        else: 
            print("connection failed")
            #connect_button.config(style="dc")

#refresh com port list
def refresh_com():
    comlist = mm.serial_ports()
    com_combobox['values'] = ()
    com_combobox['values'] = comlist
    com_combobox.set(comlist[0])


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
            print("\nerror reading register - ")
            print(AttributeError)
            print("- restarting\n")
        #mm.print_regs() #troubleshooting
        #dtstr = ((mm.pv1 - mm.sv))
        gsv.set(mm.sv)
        gpv1.set(mm.pv1)
        gpv2.set(mm.pv2)
        #dts = round(dtstr,1)
        #DtSet = str(dtstr)
        #dT.set(mm.pv1*10)

        time.sleep(0.5)
        
def up_readout(var, ind, mode):
    dis_sv['text'] = (gsv.get())/10
    dis_pv1['text'] = (gpv1.get())/10
    dis_pv2['text'] = (gpv2.get())/10
    dis_deltaT['text'] = (gpv1.get() - gsv.get())/10

#threading for continuous register reading
def start_periodic_read():
    event = Event()
    read_thread = threading.Thread(target=periodic_read)
    read_thread.daemon = True
    read_thread.start()

#selects Serial or TCP
def method_sel():
    #sel = cselect.get()
    #TCP
    if cselect.get() == 1:
        com_combobox.config(state="disabled")
        refresh_button.config(state="disabled")
        ip_entry.config(state="normal")
        port_entry.config(state="normal")
    
    #COM
    else: #cselect.get() == 1:
         com_combobox.config(state="normal")
         refresh_button.config(state="normal")
         ip_entry.config(state="disabled")
         port_entry.config(state="disabled")

########################################################################
########################################################################
##this is the beginning of the GUI interface
########################################################################
##currently using tkinter .grid() for organization
root = tk.Tk()
root.title("PCE Heater GUI")
LFont = tkFont.Font(size=24)

read = True
gsv = tk.DoubleVar(root, -10)
gpv1 = tk.DoubleVar(root, -10)
gpv2 = tk.DoubleVar(root, -10)
dT = tk.StringVar(root, "-10")

gsv.trace('w',up_readout)
gpv1.trace('w',up_readout)
gpv2.trace('w',up_readout)
dT.trace('w',up_readout)

#tabs
tab_parent = ttk.Notebook(root)
con_tab = ttk.Frame(tab_parent)
feedback_tab = ttk.Frame(tab_parent)

tab_parent.add(con_tab, text="config")
tab_parent.add(feedback_tab, text="PID control")

########################################################################
##CONFIG TAB##
########################################################################

#label for com combobox
com_label = ttk.Label(con_tab, text="COM_PORT:")
com_label.grid(row=1,column=0,padx=10,pady=5, sticky = 'e')

#find list of serial ports
comlist = mm.serial_ports()

#choose COM port/ com combobox
com_var = tk.StringVar(root)
text_var = com_var

com_combobox = ttk.Combobox(con_tab,textvariable = com_var, values = comlist)
com_combobox.grid(row=1,column=1,padx=0,pady=5)
com_combobox.set(comlist[0])

#refresh comport button
refresh_button = ttk.Button(con_tab, text='Refresh', command =refresh_com)
refresh_button.grid(row=1, column=2, padx=10, pady=5, sticky = "w")

#connect button
connect_button = ttk.Button(con_tab, text="Connect", command=init_con)
connect_button.grid(row=4, column=2, padx=10, pady=5, sticky = "w")

#connect buttion styles
con = Style()
con.configure('con',bg = 'green')
dc = Style()
dc.configure('dc', bg = 'red')

#label for Serial/TCP methodology
con_type_label = ttk.Label(con_tab, text="Connection Method:")
con_type_label.grid(row=0,column=0,padx=0,pady=5,sticky = 'e')
#spacer
spacer =ttk.Label(con_tab,text = "     ").grid(row=1,column=3,padx=100,pady=5)

#label for IP entry
ip_label = ttk.Label(con_tab,text ='IP:')
ip_label.grid(row=2, column = 0,padx=10,pady=5)

#entry box for IP
ip_entry = tk.Entry(con_tab)
ip_entry.grid(row = 2, column = 1,padx=10,pady=5)

#label for port entry
port_label = ttk.Label(con_tab,text = 'Port:')
port_label.grid(row=3, column = 0,padx=10,pady=5)
#entry box for port
port_entry = tk.Entry(con_tab)
port_entry.grid(row = 3, column = 1,padx=10,pady=5)

#label for baud rate
br_label = ttk.Label(con_tab,text = 'Baud Rate:')
br_label.grid(row=4, column = 0,padx=10,pady=5)

#combobox for baud rate
br_var = tk.IntVar(root)
br_list = [4800,9600,19200,38400,57600] 
br_combo = ttk.Combobox(con_tab, values = br_list)
br_combo.grid(row=4,column = 1,padx=10,pady=5)
br_combo.set(br_list[1])

#radiobutton for Serial/TCP
cselect = tk.IntVar()
s_radiobutton=tk.Radiobutton(con_tab, text = "Serial",variable = cselect,value = 0,command=method_sel).grid(row=0,column=1,sticky='we')
t_radiobutton=tk.Radiobutton(con_tab, text = "TCP",variable = cselect,value = 1, command=method_sel).grid(row=0,column=2,sticky='w')
cselect.set(0)
method_sel()

########################################################################
##CONTROL TAB
########################################################################
#choose set value
set_value = ttk.Label(feedback_tab,text="New Set Value (°C):")
set_value.grid(row=1, column=0, padx=0, pady=5, sticky = 'e')
sv_entry = ttk.Entry(feedback_tab)
sv_entry.insert(0,"0")
sv_entry.grid(row=1, column=1, padx=0, pady=5)

#write SV button
write_button = ttk.Button(feedback_tab, text="Write", command=write_sv)
write_button.grid(row=1, column=2, padx=0, pady=5, sticky = "w")

#line separating 

#display register values
#this is for SV
dis_sv_label = ttk.Label(feedback_tab, text = "Current Set Value (°C):", font = LFont)
dis_sv = ttk.Label(feedback_tab,text =gsv.get(), font = LFont)
dis_sv_label.grid(row=3, column=0, padx=10, pady=5,rowspan=2, columnspan=2,sticky='e')
dis_sv.grid(row=3, column=2, padx=10, pady=5,rowspan=2)

#this is for PV1
dis_pv1_label = ttk.Label(feedback_tab, text = "PV1 (°C):",font = LFont)
dis_pv1 = tk.Label(feedback_tab,text =gpv1.get(),font = LFont)
dis_pv1_label.grid(row=5, column=0, padx=10, pady=5, rowspan=2, columnspan=2,sticky='e')
dis_pv1.grid(row=5, column=2, padx=10, pady=5, rowspan=2)

#this is for PV2
dis_pv2_label = ttk.Label(feedback_tab, text = "PV2 (°C):",font = LFont)
dis_pv2 = ttk.Label(feedback_tab,text =gpv2.get(),font = LFont)
dis_pv2_label.grid(row=5, column=3, padx=1, pady=5, rowspan=2, columnspan=2, sticky='e')
dis_pv2.grid(row=5, column=5, padx=10, pady=5, rowspan=2)

#this calculates delta T and displays it
dis_deltaT_label = ttk.Label(feedback_tab, text = "PV1-SV1 ΔT (°C):",font = LFont)
dis_deltaT = ttk.Label(feedback_tab,text = dT.get(),font = LFont)
dis_deltaT_label.grid(row=3, column=3, padx=10, pady=5, rowspan=2, columnspan=2,sticky='e')
dis_deltaT.grid(row=3, column=5, padx=10, pady=5, rowspan=2)

#start plot
pv1_buffer = deque(maxlen = 180)
pv2_buffer = deque(maxlen = 180)
sv1_buffer = deque(maxlen = 180)

fig, ax = plt.subplots()
fig.set_figheight(3.2)
fig.set_figwidth(9.5)
ax.set_title("Vaporizer Temp")
line, = ax.plot([], label = "PV1", c='red')
line2, = ax.plot([], label = "PV2", c = 'blue')
line3, = ax.plot([], label = "Set Value", c = 'green')

def update_plot(frame):
        if mm.connection:
            value1 = gpv1.get()/10
            value2 = gpv2.get()/10
            value3 = gsv.get()/10

            pv1_buffer.append(value1)
            pv2_buffer.append(value2)
            sv1_buffer.append(value3)

            line.set_data(range(len(pv1_buffer)),pv1_buffer)
            line2.set_data(range(len(pv2_buffer)),pv2_buffer)
            line3.set_data(range(len(sv1_buffer)),sv1_buffer)

            ax.relim()
            ax.autoscale_view()



ani = FuncAnimation(fig, update_plot, cache_frame_data = False)
plt.tight_layout()
plt.legend()
canvas = FigureCanvasTkAgg(fig, master=feedback_tab)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=10,column=0,rowspan=3, columnspan=6,sticky='ew')

#close
def on_closing():
    if mm.client and mm.client.is_socket_open():
        mm.quit()
    
    root.quit()
    root.destroy()

#pack tabs
tab_parent.pack(expand=1, fill='both')
root.protocol("WM_DELETE_WINDOW",on_closing)
root.mainloop()