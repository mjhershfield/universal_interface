import ftd3xx
from ftd3xx.defines import *
import time

def send_raw_data(device, pipe=0x02, data=b'ABCD', suppressErrors=False):
    # Transmit the data
    transferred = 0
    while(transferred != len(data)):
        # write data to specified pipe	
        transferred += device.writePipe(pipe=pipe, data=data, datalen=len(data)-transferred)
        # check status of writing data
        status = device.getLastError()
        if(status != 0):
            device.abortPipe(pipe)
            if(not suppressErrors):
                print(f'Error with writing. Status Code {status}')
            break
    # Return number of bytes written
    return transferred

def read_raw_data(device, pipe=0x82, length=4, suppressErrors=False):
    transferred = 0
    buffread = b''
    while(transferred != length):                    
        # Check status
        status = device.getLastError()
        if(status != 0):
            device.abortPipe(pipe)
            if(not suppressErrors):
                print(f'Error with reading. Status Code {status}')
            break
        # Read data from specified pipe
        output = device.readPipeEx(pipe=pipe, datalen=(length - transferred))
        buffread = output['bytes'] + buffread
        transferred += output['bytesTransferred']
    return buffread

def construct_data_packet(pipe=0x02, peripheral_addr=0, data=b'ABC', suppressErrors=False):
    # Check that data is 3 bytes or less
    datalen = len(data)
    if(datalen > 3):
        raise Exception('Error: Too many data bytes for one packet (> 3)')
    elif(datalen == 0):
        raise Exception('Error: No data bytes in packet to send')
    # Check that the address is within the correct range
    if(peripheral_addr < 0 or peripheral_addr > 7):
        raise Exception('Error: The peripheral address is out of range (0 to 7)')
    # Construct the packet
    packet = peripheral_addr << 32-3 # address
    packet += 0 << 32-4 # config flag bit
    packet += datalen << 32-6 # num valid bytes
    packet += 3 << 32-8 # don't cares (set to 1 for now)
    packet += int.from_bytes(data, byteorder='little')
    return packet.to_bytes(4, 'little')

def send_data_packet(device, pipe=0x02, peripheral_addr=0, data=b'ABC', suppressErrors=False):
    packet = construct_data_packet(pipe, peripheral_addr, data, suppressErrors)
    return send_raw_data(device=device, pipe=pipe, data=packet, suppressErrors=suppressErrors)

def send_data(device, pipe=0x02, peripheral_addr=0, data=b'ABC'):
    # For every 3 bytes of data, send a packet
    while(len(data) >= 3):
        send_data_packet(device, pipe, peripheral_addr, data[0:3])
        data = data[3:]
    # Send the rest of the data
    if(len(data) > 0):
        send_data_packet(device, pipe, peripheral_addr, data)

def read_packet(device, pipe=0x82, suppressErrors=False):
    buffread = read_raw_data(device, pipe, length=4, suppressErrors=suppressErrors)
    if(len(buffread) > 0):
        # Check if the read packet is a configuration packet response (coming from Lycan)
        is_config = buffread[0] & 0b00010000
        # print('Bytes read:', hex(int.from_bytes(buffread, 'little')))
        return is_config, buffread
    else:
        return False, None

def write_config_reg(device, pipe=0x02, peripheral_addr=0, reg_addr=0, reg_val=0):
    # Check that register address is 3 bits
    if(reg_addr < 0 or reg_addr > 7):
        print('Error: Register address is out of range (0 to 7)')
        return None
    # Check that register value is 4 bits
    if(reg_addr < 0 or reg_addr > 15):
        print('Error: Register value is out of range (0 to 15)')
        return None
    # Check that the address is within the correct range
    if(peripheral_addr < 0 or peripheral_addr > 7):
        print('Error: The peripheral address is out of range (0 to 7)')
        return None
    # Construct the packet
    packet = peripheral_addr << 32 # address
    packet += 1 << 29 # config flag bit
    packet += 1 << 28 # read/write bit
    packet += reg_addr << 27
    packet += reg_val
    # Transmit the packet
    numBytesTransferred = send_raw_data(device=device, pipe=pipe, data=packet.to_bytes(4, 'little'))
    return numBytesTransferred

def read_config_reg(device, rx_pipe=0x82, tx_pipe=0x02, peripheral_addr=0, reg_addr=0):
    # Check that register address is 3 bits
    if(reg_addr < 0 or reg_addr > 7):
        print('Error: Register address is out of range (0 to 7)')
        return None
    # Check that the peripheral address is within the correct range
    if(peripheral_addr < 0 or peripheral_addr > 7):
        print('Error: The peripheral address is out of range (0 to 7)')
        return None
    # Construct the packet
    packet = peripheral_addr << 32 # address
    packet += 1 << 29 # config flag bit
    packet += 0 << 28 # read/write bit
    packet += reg_addr << 27
    # Transmit the packet
    send_raw_data(device=device, pipe=tx_pipe, data=packet.to_bytes(4, 'little'))
    # Receive the response
    isConfig, result = read_packet(device, rx_pipe)
    if(isConfig and len(result) != 0):
        # Parse the register value (bottom 3 bytes)
        reg_val = result['bytes'][1:]
        return reg_val