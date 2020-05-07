#!/usr/bin/python3

import serial
import matplotlib.pyplot as plt

# Open serial port using the DTR hardware handshaking mode and 57600 baud
# A timeout is useful when deciding if a response is "finished"
ser = serial.Serial('/dev/ttyUSB0', 57600, dsrdtr=True, timeout=1)  

# Ensure the scope is awake and talking
ser.write(b'*IDN?\n')
ser.flush() #flush the serial to ensure the write is sent

#let's get the response
scope_idn = ser.readline() #read a maximum of 100 bytes, the timeout should end this early

if scope_idn[0:7] != b'AGILENT':
    print("Unexpected response from Agilent scope, check your connection and try again")
    ser.close()
    exit()

# ask for data to be formatted as signed WORDs (16 bits, so -32,768 through 32,767)
ser.write(b':WAVEform:FORMat WORD\n')
ser.write(b':WAVeform:BYTeorder MSBFirst\n')
ser.write(b':WAVeform:UNSigned 0\n')

#set it to examine channel 1
ser.write(b':WAVeform:SOURce CHANnel1\n') 

#let's now read what the oscilloscope is set to
ser.write(b':WAVeform:TYPE?\n')
ser.flush()
scope_read_type = ser.readline() #TYPE? returns either NORM, PEAK, or AVER

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
scope_y_increment = float(ser.readline()) #in volts

ser.write(b':WAVeform:YORigin?\n')
ser.flush()
scope_y_origin = float(ser.readline()) #in volts

ser.write(b':WAVeform:YREFerence?\n')
ser.flush()
scope_y_reference = float(ser.readline())

# ask for 1000 data points
ser.write(b':WAVeform:POINts 1000\n')
ser.flush()

# let's now try get the data!
ser.write(b':WAVeform:DATA?\n')
ser.flush()
scope_data_bytes = ser.readline() #the response here is formated preamble,data where the preamble provides the length of the data

#the preamble is in the format #[length of length of data][length of data],[data]

scope_data_preamble_len = scope_data_bytes[1] - 48 #convert the ASCII digit to an integer

scope_data_len = int(scope_data_bytes[2:2+scope_data_preamble_len]) #the data length in bytes
print("Data length (bytes): ", scope_data_len)

print("X increment (S):", scope_x_increment)
print("X reference (S):", scope_x_reference)
print("X origin (S):", scope_x_origin)

print("Y increment (V):", scope_y_increment)
print("Y reference (V):", scope_y_reference)
print("Y origin (V):", scope_y_origin)

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
plt.title("Oscilloscope capture")
plt.xlabel("Time (S)")
plt.ylabel("Voltage (V)")
plt.show()

#be a tidy kiwi, don't forget to close your port
ser.close() 