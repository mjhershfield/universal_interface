import ftd3xx_functions as ftdi
import ftd3xx
from ftd3xx.defines import *
import threading, time, sys

turn = 'R' # Initialize the turn as R (read) to start

# String to number (bytes) method
def str_to_num(inStr):
    res = 0
    # Check if the string is in binary
    if(len(inStr) == 24 and inStr.count('1') + inStr.count('0') == 24):
        for index, c in enumerate(inStr):
            res += (2**(23 - index)) * (ord(c) - 48)
        return res
    else: # String is in hexadecimal
        if(len(inStr) != 3):
            return -1
        for index, c in enumerate(inStr):
            if(c.isdigit() or ('a' <= c <= 'f')):
                if(c.isdigit()):
                    res += (16**(2 - index)) * (ord(c) - 48)
                else:
                    res += (16**(2 - index)) * (ord(c.lower()) - 87)
            else:
                return -1 # Not a proper hex string
        return res

# Print a red CLI error message
def printError(msg):
    color = 31 # Red
    print(f'\033[{color}m\n{msg}\n\033[0m')

# Print a green CLI message
def printSuccess(msg):
    color = 32 # Green
    print(f'\033[{color}m{msg}\033[0m')

## Thread for reading from FIFO (Pauses if writing)
def read_thread(turn_lock, dev):
    global turn
    while(True):
        # Pause if it's writing's turn
        if(turn == 'R'):
            # Read from the FIFO
            data_in = ftdi.read_packet(dev)
            if(data_in != None):
                printSuccess(f'Packet received: {data_in}')

## Thread for writing data to the FIFO (Only does anything once input is received via CLI)
def write_thread(turn_lock, dev):
    global turn
    while(True):
        # Wait until user hits enter
        rawIn = input()
        # Pause reading thread once input() detected
        with turn_lock:
            turn = 'W'
        if(rawIn == 'q' or rawIn == 'quit' or rawIn == 'exit'):
            message = 'Exiting...'
            printError(message)
            sys.exit()
        packet_num = str_to_num(rawIn)
        if(packet_num != -1):
            # Convert integer packet to bytes object
            packet = packet_num.to_bytes(3, 'big')
            # Write to the FIFO
            num_bytes_written = ftdi.send_data_packet(dev, data=packet)
            print('Number of bytes written', num_bytes_written, '\n')
        else:
            message = 'Issue with input (may have too many bytes, or formatting is wrong - use binary or hex), try again.'
            printError(message)
        # Un-pause the reading thread
        with turn_lock:
            turn = 'R'

## Main thread/method
def main():
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
        message = 'Error: No devices detected. Exiting...'
        printError(message)
        sys.exit()

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

if __name__ == '__main__':
    main()