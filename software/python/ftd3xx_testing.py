import ftd3xx
from ftd3xx.defines import *
import time, sys, threading
import ftd3xx_functions as fifo
import ctypes as c
import ftd3xx._ftd3xx_win32 as _ft

def str_to_num(inStr, isHex):
    res = 0
    # Check if the string is in binary
    if(len(inStr) == 24 and not isHex):
        for index, c in enumerate(inStr):
            res += (2**(23 - index)) * (ord(c) - 48)
        return res
    else: # String is in hexadecimal
        if(len(inStr) != 4):
            return -1
        for index, c in enumerate(inStr):
            if(c.isdigit() or ('a' <= c.lower() <= 'f')):
                if(c.isdigit()):
                    res += (16**(3 - index)) * (ord(c) - 48)
                else:
                    res += (16**(3 - index)) * (ord(c.lower()) - 97)
            else:
                return -1 # Not a proper hex string
        return res

# Create a list of device info and print the number of devices
numDevices = ftd3xx.createDeviceInfoList()
devices = ftd3xx.getDeviceInfoList()
# print('Number of devices: ', numDevices)

# Pick the first device in the list (for now)
if(devices != None):
    # Create a ftd3xx device instance
    dev = ftd3xx.create(devices[0].SerialNumber, FT_OPEN_BY_SERIAL_NUMBER)
    devInfo = dev.getDeviceInfo()
    bUSB3 = dev.getDeviceDescriptor().bcdUSB >= 0x300
    dev.setPipeTimeout(0x02, 3000)
    dev.setPipeTimeout(0x82, 3000)
    dev.setSuspendTimeout(0)
    dev.abortPipe(0x82) # Flush the in pipe
    dev.flushPipe(0x82)
    # fifo.lycan_flush_in_pipe(dev)
    # Print some info about the device
    print('Device Info:')
    print(f'Type: {devInfo["Type"]}')
    print(f'ID: {devInfo["ID"]}')
    print(f'Descr.: {devInfo["Description"]}')
    print(f'Serial Num: {devInfo["Serial"]}')
    print('USB 3.0?: ', bUSB3)
else:
    raise Exception('Error: No devices detected. Exiting...')

read_t = threading.Thread(target=read_thread, args=(eventCondition, dev), daemon=True)
read_t.start()

# Try to send data to the FIFO
numBytesWritten = 0

# Write
transferred = 0
# t = fifo.write_raw_bytes(dev, 0x02, b'\x0F\x12\x34\x56')
# t += fifo.write_raw_bytes(dev, 0x02, b'\x0F\x12\x34\x56')
# t = dev.writePipe(0x02, b'\x0F\x12\x34\x56', 4)
# t += dev.writePipe(0x02, b'\x0F\x12\x34\x56', 4)
t = fifo.write_data_packet(dev, 0, b'\x12\x34\x56')
t += fifo.write_data_packet(dev, 0, b'\x12\x34\x56')
t += fifo.write_data(dev, 0, b'\x78\x9A\xBC\xDE\xEF\xFF')
print('Wrote ', t, 'bytes')

# Read
data_read = b''
for i in range(4):
    buffread = fifo.read_packet(dev)[2]
    if(buffread != None):
        data_read += buffread
    print('Status: ', dev.getLastError())
print('\n Data read:', data_read.hex())

time.sleep(10)