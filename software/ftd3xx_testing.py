import ftd3xx
from ftd3xx.defines import *
import time, sys
import ftd3xx_functions as fifo
import ctypes as c

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
    dev.setPipeTimeout(0x02, 100)
    dev.setPipeTimeout(0x82, 100)
    dev.setSuspendTimeout(0)
    # dev.setPipeTimeout(0x02, 3000)
    # dev.setPipeTimeout(0x82, 3000)
    # Print some info about the device
    print('Device Info:')
    print(f'Type: {devInfo["Type"]}')
    print(f'ID: {devInfo["ID"]}')
    print(f'Descr.: {devInfo["Description"]}')
    print(f'Serial Num: {devInfo["Serial"]}')
    print('USB 3.0?: ', bUSB3)
else:
    raise Exception('Error: No devices detected. Exiting...')

# Try to send data to the FIFO
numBytesWritten = 0
# numBytesWritten += send_data_packet(dev, pipe=0x02, peripheral_addr=0, data=b'ABC')
data = b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xAA\xBB\xCC\xDD\xEE\xFF'
# data = (0x0C0A0B0C00110011AABBCCDD).to_bytes(12, 'little')
# data = (0x0C0A0B0C00110011).to_bytes(8, 'little')
print(f'\nData to write:', data.hex())

# Write
size = 8
transferred = 0
# fifo.send_raw_data(dev, data=data)
t = dev.writePipe(0x02, data, len(data))
print('transferred ', t, 'bytes')

# Read
buffread = b''
for i in range(4):
    dbuff = c.c_buffer(len(data))
    t = dev.readPipe(0x82, data=dbuff, datalen=4)
    buffread += dbuff.raw[:t]
    print(dbuff.raw[:])
    print(dev.getLastError())
print(f'\n Data read:', buffread.hex())

# Compare write/read data
if(data == buffread):
    print('******************************   The loopback worked! Yay!   ******************************')
else:
    print('Loopback Failed :(')