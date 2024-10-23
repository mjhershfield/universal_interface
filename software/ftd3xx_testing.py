import ftd3xx
from ftd3xx.defines import *

def send_data(device, pipe=0x00, peripheral_addr=0, data=b'ABC'):
    # For every 3 bytes of data, send a packet
    while(len(data) >= 3):
        send_data_packet(device, pipe, peripheral_addr, data[0:3])
        data = data[3:]
    # Send the rest of the data
    if(len(data) > 0):
        send_data_packet(device, pipe, peripheral_addr, data)

def send_data_packet(device, pipe=0x00, peripheral_addr=0, data=b'ABC'):
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
    # Transmit the packet
    device.writePipe(pipe, packet, 32)

def read_data_packet(device, pipe=0x00):
    packet = device.readPipeEx(pipe, 32)
    return packet

def write_config_reg(device, pipe=0x00, peripheral_addr=0, reg_addr=0, reg_val=0):
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
    device.writePipe(pipe, packet, 32)

# Create a list of device info and print the number of devices
numDevices = ftd3xx.createDeviceInfoList()
devices = ftd3xx.getDeviceInfoList()
print('Number of devices: ', numDevices)

# Pick the first device in the list (for now)
if(devices != None):
    # Create a ftd3xx device instance
    dev = ftd3xx.create(devices[0].SerialNumber, FT_OPEN_BY_SERIAL_NUMBER)
    devInfo = dev.getDeviceInfo()
    # Print some info about the device
    print('Device Info:')
    print(f'Type: {devInfo["Type"]}')
    print(f'ID: {devInfo["ID"]}')
    print(f'Descr.: {devInfo["Description"]}')
    print(f'Serial Num: {devInfo["Serial"]}')
else:
    raise Exception('Error: No devices detected. Exiting...')

# Try to send data to the FIFO
send_data(dev)
print(read_data_packet(dev))