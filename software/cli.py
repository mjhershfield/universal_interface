import ftd3xx_functions as ftdi
import ftd3xx
from ftd3xx.defines import *
import threading, time, sys

turn = 'R' # Initialize the turn as R (read) to start

def read_thread(turn_lock, dev):
    global turn
    while(True):
        if(turn == 'R'):
            # Read from the FIFO
            data_in = ftdi.read_packet(dev)
            if(data_in != None):
                print(f'Packet received: {data_in}')
            else:
                with turn_lock:
                    turn = 'W'

def write_thread(turn_lock, dev):
    global turn
    while(True):
        if(turn == 'W'):
            packet = input().encode()
            if(packet == b'q' or packet == b'quit' or packet == b'exit'):
                print('\nExiting...\n')
                sys.exit()
            if(type(packet) == bytes and len(packet) == 3):
                # Write to the FIFO
                num_bytes_written = ftdi.send_data_packet(dev, data=packet)
                print('Number of bytes written', num_bytes_written, '\n')
            else:
                message = 'Wrong number of bytes entered (require 3 data bytes per packet), try again.\n'
                color = 31 # Red
                print(f'\033[{color}m{message}\033[0m')
            with turn_lock:
                turn = 'R'

# Pick the first device in the list (for now)
numDevices = ftd3xx.createDeviceInfoList()
devices = ftd3xx.getDeviceInfoList()
if(devices != None):
    # Create a ftd3xx device instance
    dev = ftd3xx.create(devices[0].SerialNumber, FT_OPEN_BY_SERIAL_NUMBER)
    devInfo = dev.getDeviceInfo()
    # Print some info about the device
    print('\nDevice Info:')
    print(f'\tType: {devInfo["Type"]}')
    print(f'\tID: {devInfo["ID"]}')
    print(f'\tDescr.: {devInfo["Description"]}')
    print(f'\tSerial Num: {devInfo["Serial"]}')
else:
    raise Exception('Error: No devices detected. Exiting...')

# Print start message
print('\nStarting Threads...\n')
print('\nType "q" or "quit" to stop the Lycan program')
print('Enter data (max of 3 characters) to write to FIFO\n')

# Create a lock (used to set whose turn it is to use the FTDI - Read or Write)
turn_lock = threading.Lock()

read_t = threading.Thread(target=read_thread, args=(turn_lock, dev,), daemon=True)
write_t = threading.Thread(target=write_thread, args=(turn_lock, dev,), daemon=True)

# Start the threads
read_t.start()
write_t.start()

# Wait for the write thread to finish (it will finish when you type q or quit in the terminal)
write_t.join()