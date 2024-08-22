# Test code for acquiring trace from BOSA

### Imports and initial setup

import numpy as np
import matplotlib.pyplot as plt
import time 
import pandas as pd

from BOSA import BOSA23095
from T3PS43203P import T3PS43203P

#    rm = visa.ResourceManager()
#    rm.list_resources()
#    print(rm.list_resources())

def checkvar(msg, slptime, checkv, checkf, *args):
    checkv = checkf(*args)
    # time.sleep(slptime)
    while(checkv != str(msg + "\r\n")):
        print(checkv)
        checkv = checkf(*args)
        time.sleep(slptime)

def flatten(iterable):
    if isinstance(iterable, tuple):
        for x in iterable:
            if isinstance(x, tuple):
                yield from flatten(x)
            else:
                yield x
    
### Power supply initializing
        
# # v_source = T3PS43203P(name=('TCPIP0::169.254.211.244::1026::SOCKET'))
# channel = 4
# voltages = np.linspace(0,5,6)


### BOSA initializing

IP= "10.10.68.64"
#    address = 'GPIB0::4::INSTR'
mode = ""
is_running = ""
laser = ""
laser_flag = False

BOSA400c = BOSA23095("LAN", IP)

if BOSA400c.get_mode()=="MAIN":
    laser_flag = True
BOSA400c.set_mode("CA")

checkvar("CA",5,mode,BOSA400c.get_mode)
# time.sleep(5)
# mode = BOSA400c.get_mode()
# while(mode != "CA\r\n"):
#     print(mode)
#     mode = BOSA400c.get_mode()
#     time.sleep(5)


BOSA400c.set_state("RUN", 1)

checkvar("ON",20,is_running,BOSA400c.get_state,"RUN")
# time.sleep(5)
# is_running = BOSA400c.get_state("RUN")
# while(is_running!="ON\r\n"):
#     print(is_running)
#     is_running = BOSA400c.get_state("RUN")
#     time.sleep(5)

# checkvar("OK",5,laser,BOSA400c.get_laser)
# time.sleep(5)
# laser = BOSA400c.get_laser()
# while(laser!="OK\r\n"):
#     print(laser)
#     laser = BOSA400c.get_laser()
#     time.sleep(5)

if laser_flag==True:
    time.sleep(60)
    laser_flag = False


### Start test
    
t = time.time()

BOSA400c.set_format("ASCII")
print(BOSA400c.get_mode()+"1")
BOSA400c.set_wavSpan("40","nm")
BOSA400c.set_normY(0)
BOSA400c.autoscaleY()

NumPoints=int(BOSA400c.get_trcount())

BOSA400c.set_format("REAL")


Trace = BOSA400c.ask_TRACE_REAL('LAN',NumPoints)


### CLose and save graph

x_axis, y_axis = zip(*Trace)
x_axis = tuple(flatten(x_axis))
y_axis = tuple(flatten(y_axis))
elapsed = time.time() - t
rootfile = "C:/BOSA/data/"
svfile = input("Input file to save: ")
svfile = str(rootfile + svfile)

BOSA400c.set_format("ASCII")

plt.plot(x_axis,y_axis)
plt.xlabel(str(BOSA400c.get_unitsX()))
plt.ylabel("dB")

print(str(elapsed) +  " seconds elapsed")

df = pd.DataFrame(zip(x_axis, y_axis), columns=['nm', 'dB'])
df.to_csv(svfile + ".csv", index = False, sep = ";")
plt.savefig(svfile)
plt.close()



# BOSA400c.set_state("RUN", 0)

# checkvar("OFF",5,is_running,BOSA400c.get_state,"RUN")
# time.sleep(5)
# is_running = BOSA400c.get_state("RUN")
# while(is_running!="OFF(\r\n"):
#     print(is_running)
#     is_running = BOSA400c.get_state("RUN")
#     time.sleep(5)
# time.sleep(5)
# laser = BOSA400c.get_laser()
# while(laser!="OK\r\n"):
#     print(laser)
#     laser = BOSA400c.get_laser()
#     time.sleep(5)

