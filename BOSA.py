#### Basic library to send commands by SCPI to the BOSA via GPIB####
#### 11/03/2024 José Carlos Guerra Copete - Arquimea Research Center ####

import socket
import visa
import logging
import struct

# create logger

log = logging.getLogger(__name__)

if(len(log.handlers) == 0): # check if the logger already exists

    # create logger

    log.setLevel(logging.DEBUG)

    

    # create console handler and set level to debug

    ch = logging.StreamHandler()

    ch.setLevel(logging.DEBUG)

    # create formatter

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch

    ch.setFormatter(formatter)

    

    # add ch to logger

    log.addHandler(ch)

class BOSA23095:
    """
    Basic library to send commands by SCPI
    
    ---------- Attributes ---------
    interfaceType : str
        "LAN" or "GPIB"
    location : str
        IP adress or GPIB adress of equipment
    portN : int
        number of the port where the interface is open (LAN)
    ----- Basic class Methods -----
    __init__(LAN/GPIB, IP, port, IDN True/False, Reset False/True)
    
    __del__()

    connectLan()

    write()

    read()

    ask()

    ask_TRACE_REAL()

    ask_TRACE_ASCII()

    read_TRACE_REAL()

    read_TRACE_ASCII()

    ------ BOSA SCPI Commands ------

    Refer to the BOSA Programming guide for a list of the commands.

    [] are optionals, where if in the middle of the command are defaulted to false,
    <> are inputs,
    | are options. For boolean inputs, one can input 1, 0, "ON" or "OFF"

    Getter commands (ending with ?) return the response
    Setter commands (with variable inputs) return 0 or an error
    
    """
    
    def __init__(self, interfaceType, location, portNo = 10000, IDN=True, Reset = False):
        """create the BOSA object and tries to establish a connection with the equipment

            Parameters:

                location      -> IP address or GPIB address of equipment.

                portN         -> no of the port where the interface is open (LAN)

        """

        self.interfaceType = interfaceType

        self.location = location

        self.portNo = portNo

        self.activeTrace = None

        
        if(interfaceType.lower() == "lan"):

            log.info("Connection to BOSA using Lan interface on %r",location)

            try:

                self.connectLan()

            except Exception as e:

                log.exception("Could not connect to BOSA device")

                print(e)

                raise e

                return

        elif(interfaceType.lower() == "gpib"):

            log.info("GPIB interface chosen to connect BOSA on %r",location)

            try:
             
                 self.instrument = visa.ResourceManager().open_resource(location)
            except Exception as e:

                log.exception("couldn't connect to device")

                print(e)

                raise e

                return

            log.info("Connected to device.")

        else:

            log.error("Interface Type " + interfaceType + " not valid")

            raise Exception("interface type invalid")

            return

        self.modes = ('MAIN', 'BOSA', 'TLS', 'CA')

        if(IDN):

            try:

                log.debug("Sending IDN to device...")

                self.write("*IDN?")

            except Exception as e:

                log.exception("Could not send *IDN? device")

                print(e)

                raise e
            

            log.debug("IDN send, waiting response...")

            try:

                response = self.read()

            except Exception as e:

                log.exception("Could read response from device")

                print(e)

                raise e
            
            print("IDN= " + response)
            
        if(Reset):

            try:

                log.info("resting device")

                self.write("*RST")

            except Exception as e:

                log.exception("Could not reset device")

                print(e)

                raise e

    def __del__(self):

        try:

            if(self.interfaceType.upper() == "LAN"):

                self.instrument.close()

            elif(self.interfaceType.upper() == "GPIB"):

                self.instrument.close()

        except Exception as e:

            log.warning("could not close interface correctly: exception %r", e.message)

    def connectLan(self):

        """ connect the instrument to a LAN """

        log.debug("creating socket")

        self.instrument = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.instrument.settimeout(30)

        try:

            log.debug("Connecting to remote socket...")

            self.instrument.connect((self.location, self.portNo)) 

        except Exception as e:

            log.exception("Could not connection to remote socket")

            print(e)

            raise e

            

        log.debug("Connected to remote socket")

        log.info("BOSA ready!")

    def write(self, command):

        """ write to equiment: independent of the interface

            Parameters:

                command -> data to send to device + \r\n

        """

        if(self.interfaceType.lower() == "lan"):

            log.debug("Sending command '" + command + "' using LAN interface...")

            try:

                self.instrument.sendall( (command + "\r\n").encode())

            except Exception as e:

                log.exception("Could not send data, command %r",command)

                print(e)

                raise e

        elif(self.interfaceType.lower() == "gpib"):

            log.debug("Sending command '" + command + "' using GPIB interface...")

            try:

                self.instrument.write(command)

            except Exception as e:

                log.exception("Could not send data, command %r",command)

                print(e)

                raise e
            
    def read(self):

        """ read something from device"""

        message = ""

        if(self.interfaceType.lower() == "lan"):

            log.debug("Reading data using LAN interface...")

            while(1):

                try:
                    data = self.instrument.recv(115200)
                    message += data.decode()

                except Exception as e:

                    log.exception("Could not read data")

                    print(e)

                    raise e

                if("\n" in message):

                    break

            log.debug("All data readed!")

        elif(self.interfaceType.lower() == "gpib"):

            log.debug("Reading data using GPIB interface...")

            while(1):

                try:

                    message = self.instrument.read()

                    if(message!=''):
                        break
                
                except Exception as e:

                    log.exception("Could not read data")

                    print(e)

                    raise e

#                if("\n" in message):
#
#                    break

            log.debug("All data readed!")

        log.debug("Data received: " + message)

        return message

    def ask(self, command):

        """ writes and reads data"""

        data = ""

        self.write(command)

        data = self.read()

        return data

    def ask_TRACE_REAL(self,interfaceType,NumPoints):

        """ writes and reads data"""
        
        data = ""

        self.write("TRAC?")

        data = self.read_TRACE_REAL(interfaceType,NumPoints)

        return data
    
    def ask_TRACE_ASCII(self):

        """ writes and reads data"""

#        data = ""
        self.write("FORM ASCII")
        data = ""

        self.write("TRAC?")
        data = self.read_TRACE_ASCII()

        return data

    def read_TRACE_REAL(self,interfaceType,NumPoints):

        """ read something from device"""

        response_byte_array=b''
        msgLength = int(NumPoints*2*8) # 8 Bytes (double) and 2 values, wavelength and power.

        log.debug("Reading data using LAN interface...")


        if(self.interfaceType.lower() == "lan"):

            while(1):
    
                try:
                    if (msgLength<19200):
                        Byte_data = self.instrument.recv(msgLength)
                    else:
                        Byte_data = self.instrument.recv(19200)
    
                    response_byte_array= b''.join([response_byte_array, Byte_data])
                    read_length=len(Byte_data)
                    msgLength=msgLength-read_length
    
                except Exception as e:
    
                    log.exception("Could not read data")
    
                    print(e)
    
                    raise e
    
                if(msgLength==0):
                    break
         
        elif(self.interfaceType.lower() == "gpib"):

            while(1):
    
                try:
                    response_byte_array = self.instrument.read_bytes(msgLength, chunk_size=None, break_on_termchar=False)
                
                    if((response_byte_array != '')):
                        break
                    
                except Exception as e:
    
                    log.exception("Could not read data")
    
                    print(e)
    
                    raise e
        
        c, r = 2, int(NumPoints)
        Trace= [[0 for x in range(c)] for x in range(r)]
        for x in range(0,int(NumPoints)):
            Trace[x][0]=struct.unpack('d', response_byte_array[(x)*16:(x)*16+8])
            Trace[x][1] = struct.unpack('d', response_byte_array[(x) * 16+8:(x+1) * 16 ])

        return Trace

    def read_TRACE_ASCII(self):

        """ read something from device"""
        log.debug("Reading data using GPIB interface...")

        while(1):

            try:
                
                Byte_data = self.instrument.read_ascii_values(converter='f', separator=',', container=list,delay=None)
            
                if((Byte_data != '')):
                    break
                
            except Exception as e:

                log.exception("Could not read data")

                print(e)

                raise e

        return Byte_data

#   Instrument identification commands
        
    def get_identificationNumber(self):
        if self.available:
            return self.ask('*IDN?')
        else:
            print("Connect to device first.")

    def is_operationComplete(self):
        if self.available:
            return self.ask('*OPC?')
        else:
            print("Connect to device first")

#   Instrument subsystem commands

    def get_mode(self):
        return self.ask("INST:STAT:MODE ?")
    
    def set_mode(self, mode):
        if mode.upper() in self.modes:
            return self.ask("INST:STAT:MODE " + mode.upper())
        else:
            print("Mode selected " + mode + " is not valid")

    def get_state(self, meas_state):
        if meas_state.upper() in ('HOLD', 'RUN'):
            return self.ask("INST:STAT:" + meas_state + " ?")
        else:
            print("Measurement state " + meas_state + " not valid")

    def set_state(self, meas_state, on):
        if meas_state.upper() in ('HOLD', 'RUN') and on in (1,0,"1","0", True, False):
            if on == True:
                on = 1
            elif on == False:
                on = 0
            return self.ask("INST:STAT:" + meas_state + " " + str(on))
        else:
            print("Measurement state " + meas_state + " or state " + on + " not valid")

#   Display subsystem commands

    def autoscaleY(self, window = False, scale = False, once = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if scale == True:
            scal = ":SCAL"
        elif scale == False:
            scal = ""
        else: 
            print("Value for scale must be boolean, instead it is " + scale)
            return
        if once == True:
            return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":AUTO ONCE")
        elif once == False:
            return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":AUTO")
        else:
            print("Value for once must be boolean, instead it is " + once)

    def set_bottomY(self, value, magnitude, window = False, scale = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if scale == True:
            scal = ":SCAL"
        elif scale == False:
            scal = ""
        else: 
            print("Value for scale must be boolean, instead it is " + scale)
        if str(magnitude or "").upper() in ("DBM", "MW", ""):
            return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":BOTT " + value + str(magnitude or "").upper())
        else:
            return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":BOTT " + value)

    def get_bottomY(self, window, scale):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if scale == True:
            scal = ":SCAL"
        elif scale == False:
            scal = ""
        else: 
            print("Value for scale must be boolean, instead it is " + scale)
            return
        return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":BOTT?")
    
    def set_powresY(self, value, magnitude, window = False, scale = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if scale == True:
            scal = ":SCAL"
        elif scale == False:
            scal = ""
        else: 
            print("Value for scale must be boolean, instead it is " + scale)
        if str(magnitude or "").upper() in ("DBM", "MW"):
            return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":PDIV " + value + str(magnitude or "").upper())
            
        else:
            return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":PDIV " + value)
                   
    def get_powresY(self, window = False, scale = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if scale == True:
            scal = ":SCAL"
        elif scale == False:
            scal = ""
        else: 
            print("Value for scale must be boolean, instead it is " + scale)
            return
        return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":PDIV?")
        
    def set_refY(self, value, magnitude, window = False, scale = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if scale == True:
            scal = ":SCAL"
        elif scale == False:
            scal = ""
        else: 
            print("Value for scale must be boolean, instead it is " + scale)
        if str(magnitude or "").upper() in ("DBM", "MW", ""):
            return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":RLEV " + value + str(magnitude or "").upper())
            
        else:
            return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":RLEV " + value)
                   
    def get_refY(self, window = False, scale = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if scale == True:
            scal = ":SCAL"
        elif scale == False:
            scal = ""
        else: 
            print("Value for scale must be boolean, instead it is " + scale)
            return
        return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":RLEV?")
        
    def set_normY(self, on, window = False, scale = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if scale == True:
            scal = ":SCAL"
        elif scale == False:
            scal = ""
        else: 
            print("Value for scale must be boolean, instead it is " + scale)
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":NORM " + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":NORM 1")
                
            elif on == False:
                return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":NORM 0")
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_normY(self, window = False, scale = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if scale == True:
            scal = ":SCAL"
        elif scale == False:
            scal = ""
        else: 
            print("Value for scale must be boolean, instead it is " + scale)
            return
        return self.ask("DISP" + wind + ":TRAC:Y" + scal + ":NORM?")
        
    def set_spacY(self, scale, window = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if str(scale).upper() in ("LOG", "LIN"):
            return self.ask("DISP" + wind + ":TRAC:Y:SPAC " + str(scale).upper())
            
        else:
            print("Value for scale must be LIN or LOG, instead it is: " + scale)

    def get_spacY(self, window = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        return self.ask("DISP" + wind + ":TRAC:Y:SPAC?")
        
    def set_unitsX(self, units, window = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if str(units).upper() in ("WAV", "FREQ"):
            return self.ask("DISP" + wind + ":TRAC:X " + str(units).upper())
            
        else:
            print("Value for units must be WAV or FREQ, instead it is: " + units)

    def get_unitsX(self, window = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        return self.ask("DISP" + wind + ":TRAC:X?")
        
    def set_trace(self, trace, on, window = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if str(trace).upper() in ("A","B","M1", "M2", "M3", "M4"):
            if str(on).upper() in ("ON", "OFF"):
                return self.ask("DISP" + wind + ":TRAC:STAT " + str(trace).upper() + " " + str(on).upper())
                
            elif on in (True, 1, "1"):
                return self.ask("DISP" + wind + ":TRAC:STAT " + str(trace).upper() + " 1")
                
            elif on in (False, 0, "0"):
                return self.ask("DISP" + wind + ":TRAC:STAT " + str(trace).upper() + " 0")
                
            else:
                print("Value for on must be ON or OFF, instead it is " + str(on).upper())
        else:
            print("Value for trace must be M1 to M4, instead it is: " + str(trace).upper())

    def get_trace(self, window = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        return self.ask("DISP" + wind + ":TRAC:STAT?")
        
    def set_graphBand(self, band, window = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if str(band).upper().replace(" ", "") in ("C", "L", "CL", "C+L"):
            return self.ask("DISP" + wind + ":GRAPHICSEL C+L")
            
        elif str(band).upper() == "O":
            return self.ask("DISP" + wind + ":GRAPHICSEL O")
            
        else:
            print("Value for band must be CL or O")

    def get_graphBand(self, window = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        return self.ask("DISP" + wind + ":GRAPHSEL ?")
        
    def set_graphView(self, band, window = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        if str(band).upper().replace(" ", "") in ("C", "L", "CL", "C+L"):
            return self.ask("DISP" + wind + ":GRAPHICVIEW C+L")
            
        elif str(band).upper() == "O":
            return self.ask("DISP" + wind + ":GRAPHICVIEW O")
            
        elif str(band).upper().replace(" ", "") in ("OC", "OL", "OCL", "CLO", "CO", "LO", "O+C+L", "C+L+O"):
            return self.ask("DISP" + wind + ":GRAPHICVIEW O+C+L")
            
        else:
            print("Value for band must be CL, O or OCL")

    def get_graphView(self, window = False):
        if window == True:
            wind = ":WIND"
        elif window == False:
            wind = ""
        else: 
            print("Value for window must be boolean, instead it is " + window)
            return
        return self.ask("DISP" + wind + ":GRAPHICVIEW ?")
        
    def set_grapSel(self, act):
        if str(act).upper() in ("A", "B", "C"):
            return self.ask("DISP:COMP:GRAPHICSEL " + str(act).upper())
        else:
            print("Value for act must be A, B or C, instead it is " + act)

    def get_graphSel(self):
        return self.ask("DISP:COMP:GRAPHSEL ?")
        
#   SENSe subsystem commands
    
    def set_wavCenter(self, units, value = "MAX"):
        if str(value).upper() == "MAX":
            return self.ask("SENS:WAV:CENT MAX")
            
        else:
            if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
                return self.ask("SENS:WAV:CENT " + value + " " + str(units or "").upper())
                
            else:
                print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def get_wavCenter(self):
        return self.ask("SENS:WAV:CENT?")
        
    def set_wavSingle(self, on):
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("SENS:WAV:SINGLE " + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("SENS:WAV:SINGLE 1")
                
            elif on == False:
                return self.ask("SENS:WAV:SINGLE 0")
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_wavSingle(self):
        return self.ask("SENS:WAV:SINGLE?")
        
    def set_wavSmooth(self, value, units):
        if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
            return self.ask("SENS:WAV:CENT " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def get_wavSmooth(self):
        return self.ask("SENS:WAV:SMOOTH?")
        
    def set_wavSpan(self, value, units):
        if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
            return self.ask("SENS:WAV:SPAN " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def get_wavSpan(self):
        return self.ask("SENS:WAV:SPAN?")
        
    def set_wavSpeed(self, value, units):
        if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
            return self.ask("SENS:WAV:SPEED " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def get_wavSpeed(self):
        return self.ask("SENS:WAV:SPEED?")
        
    def set_wavSweepCal(self, on):
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("SENS:WAV:SWEEPCAL " + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("SENS:WAV:SWEEPCAL 1")
                
            elif on == False:
                return self.ask("SENS:WAV:SWEEPCAL 0")
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_wavSweepCal(self):
        return self.ask("SENS:WAV:SWEEPCAL?")
        
    def set_wavStat(self, value, units):
        if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
            return self.ask("SENS:WAV:STAT " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def get_wavStat(self):
        return self.ask("SENS:WAV:STAT?")
        
    def set_wavStart(self, value, units):
        if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
            return self.ask("SENS:WAV:STAR " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def get_wavStart(self):
        return self.ask("SENS:WAV:STAR?")
        
    def set_wavStop(self, value, units):
        if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
            return self.ask("SENS:WAV:STOP " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def get_wavStop(self):
        return self.ask("SENS:WAV:STOP?")
        
    def set_wavRes(self, value, units):
        if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
            return self.ask("SENS:WAV:RES " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def get_wavRes(self):
        return self.ask("SENS:WAV:RES?")
        
    def set_wavSMode(self, mode):
        if str(mode).upper() in ("HR", "HS"):
            return self.ask("SENS:WAV:SMOD " + str(mode).upper())
            
        else:
            print("Value for mode must be HR or HS, instead it is " + mode)

    def get_wavSMode(self):
        return self.ask("SENS:WAV:SMOD?")
        
    def set_avgCount(self, number = "CONT"):
        if str(number).upper() in ("4", "8", "12", "32", "CONT"):
            return self.ask("SENS:AVER:COUN " + str(number).upper())
            
        else:
            print("Value for number must be 4, 8, 12, 32 or CONT , instead it is " + number)

    def get_avgCount(self):
        return self.ask("SENS:AVER:COUN?")
        
    def set_avgState(self, on):
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("SENS:AVER:STAT " + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("SENS:AVER:STAT 1")
                
            elif on == False:
                return self.ask("SENS:AVER:STAT 0")
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_avgState(self):
        return self.ask("SENS:AVER:STAT?")
          
    def set_avgCorr(self, on):
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("SENS:AVER:CORR " + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("SENS:AVER:CORR 1")
                
            elif on == False:
                return self.ask("SENS:AVER:CORR 0")
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_avgCorr(self):
        return self.ask("SENS:AVER:CORR?")
        
    def set_avgCorrCen(self, value, units):
        if str(units or "").upper() in ("NM", ""):
            return self.ask("SENS:AVER:CORR:CENT " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, instead it is " + units)

    def get_avgCorrCen(self):
        return self.ask("SENS:AVER:CORR:CENT?")
        
    def set_avgCorrSpan(self, value, units):
        if str(units or "").upper() in ("NM", ""):
            return self.ask("SENS:AVER:CORR:SPAN " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, instead it is " + units)

    def get_avgCorrSpan(self):
        return self.ask("SENS:AVER:CORR:SPAN?")
        
    def noiseZero(self):
        return self.ask("SENS:NOIS")
        
    def set_laser(self, on):
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("SENS:SWITCH " + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("SENS:SWITCH 1")
                
            elif on == False:
                return self.ask("SENS:SWITCH 0")
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_laser(self):
        return self.ask("SENS:SWITCH?")
        
    def set_sweep(self, on):
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("SENS:SWEEP " + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("SENS:SWEEP 1")
                
            elif on == False:
                return self.ask("SENS:SWEEP 0")
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_sweep(self):
        return self.ask("SENS:SWEEP?")
        
    def set_laserBand(self, band):
        if str(band).upper().replace(" ", "") in ("C", "L", "CL", "C+L"):
            return self.ask("SENS:LAS C+L")
            
        elif str(band).upper() == "O":
            return self.ask("SENS:LAS O")
            
        else:
            print("Value for band must be CL or O, instead it is " + band)

    def get_laserBand(self):
        return self.ask("SENS:LAS ?")
        
    def set_measBand(self, band):
        if str(band).upper().replace(" ", "") in ("C", "L", "CL", "C+L"):
            return self.ask("SENS:BAND C+L")
            
        elif str(band).upper() == "O":
            return self.ask("SENS:BAND O")
            
        elif str(band).upper().replace(" ", "") in ("OC", "OL", "OCL", "CLO", "CO", "LO", "O+C+L", "C+L+O"):
            return self.ask("SENS:BAND O+C+L")
            
        else:
            print("Value for band must be CL, O or OCL, instead it is "+ band)

    def get_measBand(self):
        return self.ask("SENS:BAND ?")
        
#   Input subsystem commands

    def set_inpSPar(self, meas):
        if str(meas).upper() == "IL":
            return self.ask("INP:SPAR IL")
            
        elif str(meas).upper() == "RL":
            return self.ask("INP:SPAR RL")
            
        elif str(meas).upper().replace(" ", "") in ("ILRL", "IL+RL", "IR", "RLIL", "RL+IL", "RI", "IL&RL", "RL&IL"):
            return self.ask("INP:SPAR IL&RL")
            
        else:
            print("Value for meas must be IL, RL or IL&RL, instead it is " + meas)

    def get_inpSPar(self):
        return self.ask("INP:SPAR?")
        
    def set_inpPol(self, pol):
        #1+2, 1, 2, 1&2 available on BOSA
        #PDL, MAX, MIN, SIMUL // INDEP, 1, 2, SIMuL on Component Analyzer (with/without x30)
        if str(pol).upper() in ("1+2", "1", "2", "1&2", "PDL", "MAX", "MIN", "SIMUL", "INDEP"):
            return self.ask("INP:POL " + str(pol).upper())
            
        else:
            print("Value for pol must be 1+2, 1, 2, 1&2 for BOSA and PDL, MAX, MIN, SIMUL, INDEP, 1 or 2 for CA ")

    def get_inpPol(self):
        return self.ask("INP:POL?")
        
    def set_inpMueller(self, on):
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("INP:POL:MUELL " + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("INP:POL:MUELL 1")
                
            elif on == False:
                return self.ask("INP:POL:MUELL 0")
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_inpMueller(self):
        return self.ask("INP:POL:MUELL?")
        
    def get_inpPow(self):
        return self.ask("INP:POW?")
        
#   Calculate subsystem commands

    def mrk_disable(self):
        return self.ask("CALC:MARK:AOFF")

    def set_mrkState(self, on):
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("CALC:MARK:STAT " + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("CALC:MARK:STAT 1")
                
            elif on == False:
                return self.ask("CALC:MARK:STAT 0")
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_mrkState(self):
        return self.ask("CALC:MARK:STAT?")
        
    def set_mrkMode(self, mode):
        if str(mode).upper() in ("TRCK", "FIXX", "FIXY"):
            return self.ask("CALC:MARK:MOD " + mode)
            
        else:
            print("Value for mode must be TRCK, FIXX or FIXY, instead it is " + mode)

    def get_mrkState(self):
        return self.ask("CALC:MARK:MOD?")
        
    def mrk_max(self):
        return self.ask("CALC:MARK:MAX")
        
    def mrk_maxNext(self):
        return self.ask("CALC:MARK:MAX:NEXT")
        
    def mrk_maxRight(self):
        return self.ask("CALC:MARK:MAX:RIGHT")
        
    def mrk_maxLeft(self):
        return self.ask("CALC:MARK:MAX:LEFT")
        
    def mrk_center(self):
        return self.ask("CALC:MARK:SCEN")
        
    def set_mrkX(self, value, units):
        if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
            return self.ask("CALC:MARK:X " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def get_mrkX(self):
        return self.ask("CALC:MARK:X?")
           
    def set_mrkY(self, value, units):
        if str(units or "").upper() in ("DBM", "MW", ""):
            return self.ask("CALC:MARK:Y " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be DBM or MW, instead it is " + units)

    def get_mrkY(self):
        return self.ask("CALC:MARK:Y?")
        
    def set_mrkThr(self, value, unit):
        if str(unit or "").upper() in ("DB", ""):
            return self.ask("CALC:MARK:THRE " + value + " " + str(unit or "").upper())
            
        else:
            print("Value for unit must be DB, instead it is " + unit)

    def get_mrkThr(self):
        return self.ask("CALC:MARK:THRE?")
         
    def set_mrkRout(self, meas):
        if str(meas).upper() in ("FREQ", "WAV"):
            return self.ask("CALC:MARK:READ " + str(meas).upper())
            
        else:
            print("Value for meas must be FREQ or WAV, instead it is " + meas)

    def get_mrkRout(self):
        return self.ask("CALC:MARK:READ?")
           
    def mrk_SRefLev(self):
        return self.ask("CALC:MARK:SRL")
         
    def get_mrkPol(self):
        return self.ask("CALC:MARK:FUNC:DELT:POL")
        
    def set_mrkDfun(self, on, state = False):
        if state == True:
            stat = ":STAT "
        elif state == False:
            stat = " "
        else: 
            print("Value for state must be boolean, instead it is " + state)
            return
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("CALC:MARK:FUNC:DELT" + stat + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("CALC:MARK:FUNC:DELT" + stat + 1)
                
            elif on == False:
                return self.ask("CALC:MARK:FUNC:DELT" + stat + 0)
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_mrkDfun(self, state = False):
        if state == True:
            stat = ":STAT "
        elif state == False:
            stat = " "
        else: 
            print("Value for state must be boolean, instead it is " + state)
            return
        return self.ask("CALC:MARK:FUNC:DELT" + stat + "?")
        
    def mrkD_Reset(self):
        return self.ask("CALC:MARK:FUNC:DELT:RES")
        
    def get_mrkDXOff(self):
        return self.ask("CALC:MARK:FUNC:DELT:X:OFFS?")
         
    def get_mrkDXRef(self):
        return self.ask("CALC:MARK:FUNC:DELT:X:REF?")
        
    def get_mrkDYOff(self):
        return self.ask("CALC:MARK:FUNC:DELT:Y:OFFS?")
        
    def get_mrkDYRef(self):
        return self.ask("CALC:MARK:FUNC:DELT:Y:REF?")
         
    def get_mrkDPol(self):
        return self.ask("CALC:MARK:FUNC:DELT:POL?")
        
    def get_mrkDAng(self):
        return self.ask("CALC:MARK:FUNC:DELT:ANG?")
    
    def set_maxHold(self, on, state):
        if state == True:
            stat = ":STAT "
        elif state == False:
            stat = " "
        else: 
            print("Value for state must be boolean, instead it is " + stat )
            return
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("CALC:MAX" + stat + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("CALC:MAX" + stat + 1)
                
            elif on == False:
                return self.ask("CALC:MAX" + stat + 0)
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_maxHold(self, state):
        if state == True:
            stat = ":STAT "
        elif state == False:
            stat = " "
        else: 
            print("Value for state must be boolean, instead it is " + stat)
            return
        return self.ask("CALC:MAX" + stat)
        
    def set_minHold(self, on, state):
        if state == True:
            stat = ":STAT "
        elif state == False:
            stat = " "
        else: 
            print("Value for state must be boolean, instead it is " + stat )
            return
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("CALC:MIN" + stat + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("CALC:MIN" + stat + 1)
                
            elif on == False:
                return self.ask("CALC:MIN" + stat + 0)
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_maxHold(self, state):
        if state == True:
            stat = ":STAT "
        elif state == False:
            stat = " "
        else: 
            print("Value for state must be boolean, instead it is " + stat)
            return
        return self.ask("CALC:MIN" + stat)
        
    def set_TPow(self, on):
        if str(on).upper() in ("1", "0", "ON", "OFF"):
            return self.ask("CALC:TPOW" + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("CALC:TPOW 1")
                
            elif on == False:
                return self.ask("CALC:TPOW 0")
                
        else:
            print("Value for on must be 1, 0, ON, OFF or a boolean, instead it is " + on)

    def get_TPow(self, data):
        if data == True:
            dat = ":DATA?"
        elif data == False:
            dat = "?"
        else: 
            print("Value for data must be boolean, instead it is " + data)
            return
        return self.ask("CALC:TPOW" + dat)
        
    def set_TPowUp(self, value, units):
        if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
            return self.ask("CALC:TPOW:IRAN:UPP " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def get_TPowUp(self):
        return self.ask("CALC:TPOW:IRAN:UPP?")
        
    def set_TPowLow(self, value, units):
        if str(units or "").upper() in ("NM", "PM", "GHZ", "THZ", ""):
            return self.ask("CALC:TPOW:IRAN:LOW " + value + " " + str(units or "").upper())
            
        else:
            print("Value for units must be NM, PM, GHZ or THZ, instead it is " + units)

    def set_TPowLow(self):
        return self.ask("CALC:TPOW:IRAN:LOW?")
        
    def get_auxInPow(self):
        return self.ask("CALC:AUXIN:POW?")
        
    def set_OSNR(self, on):
        if str(on).upper() in ("ON", "OFF"):
            return self.ask("CALC:OSNR:STAT " + str(on).upper())
            
        elif isinstance(on, bool):
            if on == True:
                return self.ask("CALC:TPOW ON")
                
            elif on == False:
                return self.ask("CALC:TPOW OFF")
                
        else:
            print("Value for on must be ON or OFF or a boolean, instead it is " + on)

    def get_OSNR(self):
        return self.ask("CALC:OSNR:STAT?")
        
    def get_OSNRval(self):
        return self.ask("CALC:OSNR:VALUE?")
        
    def set_OSNRdist(self, value):
        return self.ask("CALC:OSNR:DIST " + value)
        
    def get_OSNRdist(self):
        return self.ask("CALC:OSNR:DIST?")
        
    def set_OSNRNmode(self, mode):
        if str(mode).upper() in ("PEAK", "BW"):
            return self.ask("CALC:OSNR:NOISEPOWMODE" + str(mode).upper())
            
        else:
            print("Value for mode must be Peak or BW, it is instead " + mode)

    def get_OSNRNmode(self):
        return self.ask("CALC:OSNR:NOISEPOWMODE?")
                
    def set_OSNRNrefBw(self, value):
        return self.ask("CALC:OSNR:NOISEREFBW " + value)
           
    def get_OSNRNrefBW(self):
        return self.ask("CALC:OSNR:NOISEREFBW?")
           
    def set_OSNRSmode(self, mode):
        if str(mode).upper() in ("PEAK", "BW"):
            return self.ask("CALC:OSNR:SIGNALPOWMODE" + str(mode).upper())
            
        else:
            print("Value for mode must be Peak or BW, it is instead " + mode)

    def get_OSNRSmode(self):
        return self.ask("CALC:OSNR:SIGNALPOWMODE?")
    
    def set_OSNRSrefBw(self, value):
        return self.ask("CALC:OSNR:SIGNALBW " + value)
          
    def get_OSNRSrefBW(self):
        return self.ask("CALC:OSNR:SIGNALBW?")      
    
#   Trace subsystem commands

    def get_trcount(self, data = False):
        if data == True:
            dat = ":DATA"
        elif data == False:
            dat = ""
        else: 
            print("Value for data must be boolean, instead it is " + data)
            return
        return self.ask("TRAC" + dat + ":COUNT?")
         
    def get_trace(self, data = False):
        if data == True:
            dat = ":DATA?"
        elif data == False:
            dat = "?"
        else: 
            print("Value for data must be boolean, instead it is " + data)
            return
        return self.ask("TRAC" + dat)
    
    def get_trMaxX(self, data = False):
        if data == True:
            dat = ":DATA"
        elif data == False:
            dat = ""
        else: 
            print("Value for data must be boolean, instead it is " + data)
            return
        return self.ask("TRAC" + dat + ":MAX:X?")
    
    def get_trMaxY(self, data = False):
        if data == True:
            dat = ":DATA"
        elif data == False:
            dat = ""
        else: 
            print("Value for data must be boolean, instead it is " + data)
            return
        return self.ask("TRAC" + dat + ":MAX:Y?")

#   Format subsystem commands

    def set_format(self, format, length=-1, data = False):
        if data == True:
            dat = ":DATA"
        elif data == False:
            dat = ""
        else: 
            print("Value for data must be boolean, instead it is " + data)
            return
        if str(format).upper() == "ASCII":
            if length != -1:
                return self.ask("FORM" + dat + " ASCII," + int(length))
            else:
                return self.ask("FORM" + dat + " ASCII")
        elif str(format).upper() == "REAL":
            return self.ask("FORM" + dat + " REAL")
        else:
            print("Value for format must be ASCII or REAL, instead it is " + format)

        return self.ask("FORM" + dat)

    def get_format(self, data = False):
        if data == True:
            dat = ":DATA?"
        elif data == False:
            dat = "?"
        else: 
            print("Value for data must be boolean, instead it is " + data)
            return
        return self.ask("FORM" + dat)

#   MMemory subsystem commands

    def store_tr(self, name, ftype, ink):
        if str(ftype).upper() not in ("BDF", "TXT", "CSV", "JPG", "BMP", "GIF", "TIF"):
            print("Value for ftype must be bdf, txt, csv, jpg, bmp, gif or tif, instead it is " + ftype)
            return
        else:
            if str(ink).upper() in ("1", "0", "ON", "OFF"):
                return self.ask("MMEM:STOR:TRAC " + name + "." + ftype + ", " + str(ink).upper())
                
            elif isinstance(ink, bool):
                if ink == True:
                    return self.ask("MMEM:STOR:TRAC " + name + "." + ftype + ", 1")
                elif ink == False:
                    return self.ask("MMEM:STOR:TRAC " + name + "." + ftype + ", 0")
            else:
                print("Value for ink must be 1, 0, ON, OFF or a boolean, instead it is " + ink)
                return

    def del_tr(self, name):
        return self.ask("MMEM:DEL:TRAC " + name)
    
    def load_tr(self, trace, name):
        if str(trace).upper() not in ("M1", "M2", "M3", "M4"):
            print("Value for trace must be M1 to M4, it is instead " + trace)
            return
        else:
            return self.ask("MMEM:LOAD:TRAC " + trace + "," + name)