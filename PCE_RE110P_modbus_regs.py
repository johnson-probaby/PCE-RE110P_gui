##this file contains the relevant modbus register addresses for our control application

#holding regs
TC1_type = 0 # 0 = B tp Thermocouple 1 = E, 2 = J, 3 = K, 4 = L, 5 = N, 6 = R, 7 = S, 8 = T, 9 = U, 10 = Pt100, 11= NTC, 12 = 0-20 mA, 13 = 4-20 mA, 14 = 0-5 V, 15 = 1-5 V, 16 = 0-10 V, 17 = 0-150 mV, 18 = 0-550 Ohm, 19 = 0-10 kOhm
TC2_type = 9 # 0 = B tp Thermocouple 1 = E, 2 = J, 3 = K, 4 = L, 5 = N, 6 = R, 7 = S, 8 = T, 9 = U, 10 = Pt100, 11= NTC, 12 = 0-20 mA, 13 = 4-20 mA, 14 = 0-5 V, 15 = 1-5 V, 16 = 0-10 V, 17 = 0-150 mV, 18 = 0-550 Ohm, 19 = 0-10 kOhm
SV1 = 133 #Set Value 1 - takes: word
SV2 = 134 #Set Value 2 - takes: word

#input regs
PV1 = 0 #Process Value 1 - gives: word -VALUE MUST BE DIVIDED BY 10 e.g. For example; If temp is 32.5°C , 325 wll be read over modbus
PV2 = 1 #Process Value 2 - gives: word -VALUE MUST BE DIVIDED BY 10 e.g. For example; If temp is 32.5°C , 325 wll be read over modbus
NTC = 2 #internal temp - gives: word -VALUE MUST BE DIVIDED BY 10 e.g. For example; If temp is 32.5°C , 325 wll be read over modbus

#coil regs

#discreet input regs
ssr1_OS = 3 #ssr1 output status - gives: bit
prob1_FS = 4 #probe 1 failure status - gives: bit
prob2_FS = 9 #probe 2 failure status - gives: bit