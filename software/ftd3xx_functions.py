import ftd3xx
from ftd3xx.defines import *
import time

def write_raw_bytes(device, pipe=0x02, raw=b'ABCD', suppressErrors=False):
    """
    Summary:
        Sends bytes to the FT601 device using the writePipe call until an error (eg. timeout) occurs or all bytes are transferred.

    Args:
        device: FT601 FTD3XX Instance
        pipe (int, optional): Pipe of the FT601 to write to. Defaults to 0x02.
        raw (bytes, optional): Bytes to write. Defaults to b'ABCD'.
        suppressErrors (bool, optional): Option to suppress errors from being printed. Defaults to False.

    Returns:
        int: number of successfully transferred bytes
    """
    # Transmit the data
    transferred = 0
    while(transferred != len(raw)):
        # write data to specified pipe	
        transferred += device.writePipe(pipe=pipe, data=raw, datalen=len(raw)-transferred)
        # check status of writing data
        status = device.getLastError()
        if(status != 0):
            device.abortPipe(pipe)
            if(not suppressErrors):
                print(f'Error with writing. Status Code {status}')
            break
    # Return number of bytes written
    return transferred

def read_raw_bytes(device, pipe=0x82, length=4, suppressErrors=False):
    """
    Summary:
        Reads bytes from the FT601 device using the readPipeEx call until an error (eg. timeout) occurs or 'length' bytes are transferred.

    Args:
        device: FT601 FTD3XX Instance
        pipe (int, optional): Pipe of the FT601 to read from. Defaults to 0x82.
        length (int, optional): Number of bytes to read. Defaults to 4 (one lycan packet).
        suppressErrors (bool, optional): Option to suppress errors from being printed. Defaults to False.

    Returns:
        bytes: Bytes object of the read bytes
    """
    transferred = 0
    buffread = b''
    while(transferred != length):                    
        # Read data from specified pipe
        output = device.readPipeEx(pipe=pipe, datalen=(length - transferred))
        # Check status
        status = device.getLastError()
        if(status != 0):
            device.abortPipe(pipe)
            if(not suppressErrors):
                print(f'Error with reading. Status Code {status}')
            break
        # Store result
        buffread = output['bytes'] + buffread
        transferred += output['bytesTransferred']
    return buffread

def construct_data_packet(peripheral_addr=0, data=b'ABC'):
    """
    Summary:
        Constructs a Lycan data packet (defined in the Github documentation). Does not actually read/write anything.

    Args:
        peripheral_addr (int, optional): Peripheral to construct the data packet for (0-7). Defaults to 0.
        data (bytes, optional): 3 bytes of data to write. Defaults to b'ABC'.

    Returns:
        bytes: Little-endian bytes object of the constructed packet (4 bytes)
    """
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

def write_data_packet(device, pipe=0x02, peripheral_addr=0, data=b'ABC', suppressErrors=False):
    """
    Summary:
        Writes a Lycan data packet to the FT601 device. Uses construct_data_packet and write_raw_bytes to do so.

    Args:
        device: FT601 FTD3XX Instance
        pipe (int, optional): Pipe of the FT601 to write to. Defaults to 0x02.
        peripheral_addr (int, optional): Peripheral to construct the data packet for (0-7). Defaults to 0.
        data (bytes, optional): Bytes object of length <=3 to include in the data packet
        suppressErrors (bool, optional): Option to suppress errors from being printed. Defaults to False.

    Returns:
        int: Number of raw bytes transferred (4 = Success)
    """
    packet = construct_data_packet(peripheral_addr, data)
    return write_raw_bytes(device=device, pipe=pipe, raw=packet, suppressErrors=suppressErrors)

def write_data(device, pipe=0x02, peripheral_addr=0, data=b'ABC', suppressErrors=False):
    """
    Summary:
        Writes multiple Lycan data packets to the FT601 device. Uses write_data_packet to do so.

    Args:
        device: FT601 FTD3XX Instance
        pipe (int, optional): Pipe of the FT601 to write to. Defaults to 0x02.
        peripheral_addr (int, optional): Peripheral to construct the data packet for (0-7). Defaults to 0.
        data (bytes, optional): Bytes object of length >=3 to include in the data packet(s)
        suppressErrors (bool, optional): Option to suppress errors from being printed. Defaults to False.
    """
    # For every 3 bytes of data, send a packet
    while(len(data) >= 3):
        write_data_packet(device, pipe, peripheral_addr, data[0:3], suppressErrors=suppressErrors)
        data = data[3:]
    # Send the rest of the data
    if(len(data) > 0):
        write_data_packet(device, pipe, peripheral_addr, data, suppressErrors=suppressErrors)

def read_packet(device, pipe=0x82, suppressErrors=False):
    """
    Summary:
        Reads a Lycan packet (data or config type) from the FT601 device using read_raw_bytes.

    Args:
        device: FT601 FTD3XX Instance
        pipe (int, optional): Pipe of the FT601 to read from. Defaults to 0x82.
        suppressErrors (bool, optional): Option to suppress errors from being printed. Defaults to False.

    Returns:
        [bool, bytes|None]: [True if read packet is a config packet, Packet read from Lycan or None if read failed]
    """
    buffread = read_raw_bytes(device, pipe, length=4, suppressErrors=suppressErrors)
    if(len(buffread) > 0):
        # Check if the read packet is a configuration packet response (coming from Lycan)
        is_config = buffread[0] & 0b00010000
        # print('Bytes read:', hex(int.from_bytes(buffread, 'little')))
        return is_config, buffread
    else:
        return False, None

def write_config_command(device, pipe=0x02, peripheral_addr=0, write=True, reg_addr=0, reg_val=0):
    """
    Summary:
        Writes a Lycan configuration packet (read register or write to register) to the FT601 device. Uses write_raw_bytes.

    Args:
        device: FT601 FTD3XX Instance
        pipe (int, optional): Pipe of the FT601 to write to. Defaults to 0x02.
        peripheral_addr (int, optional): Peripheral to construct the configuration packet for (0-7). Defaults to 0.
        write (bool, optional): Whether the configuration packet is a write packet (meaning changing a Lycan peripheral config register). Defaults to True (write register).
        reg_addr (int, optional): Address of the config register to read or write. Defaults to 0.
        reg_val (int, optional): If the command is a write, the value to write to the config register. Defaults to 0.

    Returns:
        int: Number of raw bytes transferred (4 = Success, None = Error)
    """
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
    packet += write << 28 # read/write bit
    packet += reg_addr << 27
    packet += reg_val
    # Transmit the packet
    numBytesTransferred = write_raw_bytes(device=device, pipe=pipe, raw=packet.to_bytes(4, 'little'))
    return numBytesTransferred