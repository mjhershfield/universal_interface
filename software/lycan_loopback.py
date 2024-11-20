import argparse
import ftd3xx
from ftd3xx.defines import *
import ftd3xx_functions as fifo
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

def main(loopCount):
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

    successCount = 0
    for run in range(loopCount):
        # Try to send data to the FIFO
        data = b'\x01\x23\x45'
        fifo.send_data_packet(device=dev, pipe=0x02, peripheral_addr=0, data=data)
        isConfig, readData = fifo.read_packet(device=dev, pipe=0x82)

        # Compare write/read data
        if(readData != None and data == int.from_bytes(readData, 'big')):
            loopCount += 1
            print('******************************   The loopback worked! Yay!   ******************************')
        else:
            print('Loopback Failed :(')
    
    print(f'\n\n\n**********\tNumber of successes: {successCount}\t({successCount/loopCount}%)\t**********\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="data loopback demo application")
    parser.add_argument('-l', '--loop_count', type=int, default=1, help="number of tests to run (default is 1)")
    args = parser.parse_args()
    main(args.loop_count)