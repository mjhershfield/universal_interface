import ftd3xx
from ftd3xx.defines import *
import time

def send_data(device, pipe=0x82, peripheral_addr=0, data=b'ABC'):
    # For every 3 bytes of data, send a packet
    while(len(data) >= 3):
        send_data_packet(device, pipe, peripheral_addr, data[0:3])
        data = data[3:]
    # Send the rest of the data
    if(len(data) > 0):
        send_data_packet(device, pipe, peripheral_addr, data)

def send_data_packet(device, pipe=0x82, peripheral_addr=0, data=b'ABC'):
    # Check that data is 3 bytes or less
    if(len(data) > 3):
        raise Exception('Error: Too many data bytes for one packet (> 3)')
    elif(len(data) == 0):
        raise Exception('Error: No data bytes in packet to send')
    # Check that the address is within the correct range
    if(peripheral_addr < 0 or peripheral_addr > 7):
        raise Exception('Error: The peripheral address is out of range (0 to 7)')
    # Construct the packet
    packet = peripheral_addr << 32 # address
    packet += 0 << 29 # config flag bit
    packet += len(data) << 28 # num valid bytes
    packet += 3 << 26 # don't cares (set to 1 for now)
    packet += int.from_bytes(data, byteorder='big')
    # Print the packet - DEBUG
    print('Packet to be transmitted:', packet)
    # Transmit the packet
    numBytesWritten = device.writePipe(pipe, packet, 4)
    # Print result
    if(numBytesWritten > 0):
        print('Bytes transferred (written to FIFO): ', numBytesWritten)
    # Return number of bytes written
    return numBytesWritten

def read_packet(device, pipe=0x02):
    packet = device.readPipeEx(pipe, 4)
    if(packet['bytesTransferred'] > 0):
        # Check if the read packet is a configuration packet response (coming from Lycan)
        is_config = packet[0] & 0b00010000
        print('Bytes read:', packet['bytesTransferred'])
        return is_config, packet
    else:
        return None

def write_config_reg(device, pipe=0x82, peripheral_addr=0, reg_addr=0, reg_val=0):
    # Check that register address is 3 bits
    if(reg_addr < 0 or reg_addr > 7):
        raise Exception('Error: Register address is out of range (0 to 7)')
    # Check that register value is 4 bits
    if(reg_addr < 0 or reg_addr > 15):
        raise Exception('Error: Register value is out of range (0 to 15)')
    # Check that the address is within the correct range
    if(peripheral_addr < 0 or peripheral_addr > 7):
        raise Exception('Error: The peripheral address is out of range (0 to 7)')
    # Construct the packet
    packet = peripheral_addr << 32 # address
    packet += 1 << 29 # config flag bit
    packet += 1 << 28 # read/write bit
    packet += reg_addr << 27
    packet += reg_val
    # Transmit the packet
    device.writePipe(pipe, packet, 4)
    # Read the result

def read_config_reg(device, pipe=0x02, peripheral_addr=0, reg_addr=0):
    # Check that register address is 3 bits
    if(reg_addr < 0 or reg_addr > 7):
        raise Exception('Error: Register address is out of range (0 to 7)')
    # Check that the peripheral address is within the correct range
    if(peripheral_addr < 0 or peripheral_addr > 7):
        raise Exception('Error: The peripheral address is out of range (0 to 7)')
    # Construct the packet
    packet = peripheral_addr << 32 # address
    packet += 1 << 29 # config flag bit
    packet += 0 << 28 # read/write bit
    packet += reg_addr << 27
    # Transmit the packet
    device.writePipe(pipe, packet, 4)
    # Receive the response
    result = device.readPipeEx(pipe, 4)
    # Parse the register value (bottom 3 bytes)
    reg_val = result[1:]