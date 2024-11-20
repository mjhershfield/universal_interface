import ftd3xx
from ftd3xx.defines import *
import time, sys

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
data = 0x0C0A0B0C00110011AABBCCDD
print(f'\nData to write: {hex(data)}\n')

# Write
size = 12
transferred = 0
while (transferred != size):
    # write data to specified pipe	
    transferred += dev.writePipe(pipe=0x02, data=data, datalen=size-transferred)
    
    # check status of writing data
    status = dev.getLastError()
    if (status != 0):
        dev.abortPipe(0x02)
        print(f'Error with writing. Status Code {status}')
        break
print(f'Wrote {transferred} bytes.\n')

# Read
size = transferred
transferred = 0
buffread = b''
while(transferred != size):                    
    # read data from specified pipe
    output = dev.readPipeEx(pipe=0x82, datalen=(size - transferred))
    buffread += output['bytes']
    transferred += output['bytesTransferred']

    status = dev.getLastError()
    if (status != 0):
        dev.abortPipe(0x82)
        break
print(f'Read {transferred} bytes.')
print(buffread.hex())

# Compare write/read data
if(data == int.from_bytes(buffread, 'big')):
    print('******************************   The loopback worked! Yay!   ******************************')
else:
    print('Loopback Failed :(')