import PCE_RE110P_modbus_regs as rgs
import pymodbus
import serial
from pymodbus.pdu import ModbusRequest
from pymodbus.client import ModbusSerialClient as ModbusClient #initialize a serial RTU client instance
from pymodbus.client import ModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer
import logging
import time
import numpy as np
import sys
import glob

logging.basicConfig()
log = logging.getLogger()
#log.setLevel(logging.DEBUG)

sv = -10
tc1_stat = False
tc2_stat = False
ssr_stat = False
pv1 = -10
pv2 = -10

client = None
connection = False
#count= the number of registers to read
#unit= the slave unit this request is targeting
#address= the starting address to read from

#this updates the global vars for operating registers
def update_regs():
    global sv,pv1,pv2,tc1_stat,tc2_stat,ssr_stat, client
    #Starting add, num of reg to read, slave unit.
    #update TC values
    pv1  = client.read_input_registers(rgs.PV1,count=1,slave=0x01).registers[0]/10 # address, count, slave address
    pv2 = client.read_input_registers(rgs.PV2,count=1,slave=0x01).registers[0]/10 # address, count, slave address
    #read setpoint
    sv  = client.read_holding_registers(rgs.SV1,count=1,slave=0x01).registers[0]/10 # address, count, slave address
    #check sys status
    tc1_fail = client.read_discrete_inputs(rgs.prob1_FS,slave=0x01).bits[0]
    tc2_fail = client.read_discrete_inputs(rgs.prob2_FS,slave=0x01).bits[0]
    ssr_act = client.read_discrete_inputs(rgs.ssr1_OS,slave=0x01).bits[0]

    #convert bool to relevant string
    if tc1_fail: tc1_stat = "probe1 failure"
    else: tc1_stat = "normal"

    if tc2_fail: tc2_stat = "probe2 failure"
    else: tc2_stat = "normal"

    if ssr_act: ssr_stat = "active"
    else: ssr_stat = "inactive"

#updates process setvalue
def update_sv(new_sv):
    global client
    client.write_register(rgs.SV1, new_sv, slave=0x01)
    time.sleep(0.5)
    #sv  = client.read_holding_registers(rgs.SV1,count=1,slave=0x01)

#prints reg values - mostly debug
def print_regs():
    print ('sv: ', sv)
    print ('pv1: ', pv1)
    print ('pv2: ', pv2)
    print ('tc1_stat: ', tc1_stat)
    print ('tc2_stat: ', tc2_stat)
    print ('ssr_stat: ', ssr_stat)

def basic_test():
    connect_port("COM4")
    update_regs()
    print_regs()
    print("\nupdated sv: \n")
    update_sv(np.random.randint(0,9000))
    update_regs()
    print_regs()
    quit()

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def connect_port(com_port):
    global client, connection
    client= ModbusClient(method = "rtu", port=com_port,stopbits = 1, bytesize = 8, parity = 'N', baudrate= 38400, unit=1)
    connection = client.connect()
    connection = client.connected
    #print(connection)
    test  = client.read_holding_registers(rgs.SV1,count=1,slave=0x01)
    str_test = str(test)
    print("\nconnection test result: ",test)
    if "Error" in str_test:
        return False
    else: return connection

def connect_TCP(ip):
    global client, connection
    client= ModbusTcpClient(method = "rtu", host=ip, port=502, stopbits = 1, bytesize = 8, parity = 'N', baudrate= 38400, unit=1)
    connection = client.connect()
    connection = client.connected
    #print(connection)
    test  = client.read_holding_registers(rgs.SV1,count=1,slave=0x01)
    str_test = str(test)
    print("\nconnection test result: ",test)
    if "Error" in str_test:
        return False
    else: return connection

#basic_test()



#Closes the underlying socket connection
def quit():
    global client
    client.close()