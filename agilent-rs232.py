#!/usr/bin/python3

import serial
import matplotlib.pyplot as plt
import argparse

# Initiate the parser
parser = argparse.ArgumentParser()

#defaults
port = "/dev/ttyUSB0"
baud = 57600
channel = 1
length = 1000

# Add arguments
parser.add_argument("--port", "-p", help="set serial port (default %s)" % port)
parser.add_argument("--baud", "-b", help="set serial baud rate (default %d)" % baud)
parser.add_argument("--channel", "-c", help="set probe channel (default %d)" % channel)
parser.add_argument("--length", "-l", help="number of samples (default %d)" % length)

# Read arguments from the command line
args = parser.parse_args()

# Evaluate given options
if args.port:
    port = args.port
if args.baud:
    baud = int(args.baud)
if args.channel:
    channel = int(args.channel)
if args.length:
    if args.length in ("100", "250", "500", "1000", "2000", "MAXimum"):
        length = args.length
    else:
        print("Invalid length (must be in {100, 250, 500, 1000, 2000, MAXimum}")
        exit(1)
    

# Open serial port using the DTR hardware handshaking mode and 57600 baud
# A timeout is useful when deciding if a response is "finished"
ser = serial.Serial(port, baud, dsrdtr=True, timeout=1)  

# Ensure the scope is awake and talking
ser.write(b'*IDN?\n')
ser.flush() #flush the serial to ensure the write is sent

#let's get the response
scope_idn = ser.readline() 

if scope_idn[0:7] != b'AGILENT':
    print("Unexpected response from Agilent scope, check your connection and try again")
    ser.close()
    exit()

# ask for data to be formatted as signed WORDs (16 bits, so -32,768 through 32,767)
ser.write(b':WAVEform:FORMat WORD\n')
ser.write(b':WAVeform:BYTeorder MSBFirst\n')
ser.write(b':WAVeform:UNSigned 0\n')

# ask for 1000 data points
pointsString = ":WAVeform:POINts %s\n" % length
ser.write(pointsString.encode())

#set it to examine channel 1 or channel 2
if channel == 1:
    ser.write(b':WAVeform:SOURce CHANnel1\n') 
else:
    ser.write(b':WAVeform:SOURce CHANnel2\n') 

#let's now read what the oscilloscope is set to
ser.write(b':WAVeform:TYPE?\n')
ser.flush()
scope_read_type = ser.readline()[:-1] #TYPE? returns either NORM, PEAK, or AVER followed by a \n

#load dispay parameters. All of these return "NR3" format, which is a float-type
ser.write(b':WAVeform:XINCrement?\n') 
ser.flush()
scope_x_increment = float(ser.readline())

ser.write(b':WAVeform:XORigin?\n')
ser.flush()
scope_x_origin = float(ser.readline())

ser.write(b':WAVeform:XREFerence?\n')
ser.flush()
scope_x_reference = float(ser.readline())

ser.write(b':WAVeform:YINCrement?\n')
ser.flush()
scope_y_increment = float(ser.readline()) 

ser.write(b':WAVeform:YORigin?\n')
ser.flush()
scope_y_origin = float(ser.readline()) 

ser.write(b':WAVeform:YREFerence?\n')
ser.flush()
scope_y_reference = float(ser.readline())

ser.flush()

# let's now try get the data!
ser.write(b':WAVeform:DATA?\n')
ser.flush()
scope_data_bytes = ser.readline() #the response here is formated preamble,data where the preamble provides the length of the data

#we're done with the scope - be a tidy kiwi, don't forget to close the port
ser.close() 

print("Oscilloscope mode: ",scope_read_type.decode())

print("X increment (S):", scope_x_increment)
print("X reference (S):", scope_x_reference)
print("X origin (S):", scope_x_origin)

print("Y increment (V):", scope_y_increment)
print("Y reference (V):", scope_y_reference)
print("Y origin (V):", scope_y_origin)

#the preamble is in the format #[length of length of data][length of data],[data]
scope_data_preamble_len = scope_data_bytes[1] - 48 #convert the ASCII digit to an integer
scope_data_len = int(scope_data_bytes[2:2+scope_data_preamble_len]) #the data length in bytes
print("Data length (bytes): ", scope_data_len)

data_points = []
for i in range(0, scope_data_len, 2):
    data_offset = i+scope_data_preamble_len + 2
    data_point = int.from_bytes(scope_data_bytes[data_offset:data_offset+2], byteorder='big', signed=True)

    #using the formula from the agilent 5000 series programmer's guide reference manual page 595
    # voltage = [(data value - yreference) * yincrement] + yorigin
    data_point_voltage = ((data_point - scope_y_reference) * scope_y_increment) + scope_y_origin
    data_points.append(data_point_voltage)


print("Min (V):", min(data_points))
print("Max (V):", max(data_points))

data_points_times = []
for i in range(0, len(data_points)):
    #using the formula from the agilent 5000 series programmer's guide reference manual page 595
    # time = [(data point number - xreference) * xincrement] + xorigin
    data_point_time = ((i - scope_x_reference) * scope_x_increment) + scope_x_origin
    data_points_times.append(data_point_time)

#now we want to graph it
plt.plot(data_points_times, data_points)
plt.title("Oscilloscope capture (mode: "+scope_read_type.decode()+")")
plt.xlabel("Time (S)")
plt.xticks(rotation=45)
plt.ylabel("Voltage (V)")
plt.tight_layout()
plt.show()

