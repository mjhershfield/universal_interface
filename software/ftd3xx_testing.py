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
    else:
        raise Exception('Error: No data was written to the FIFO')

def read_packet(device, pipe=0x02):
    packet = device.readPipeEx(pipe, 4)
    print(packet)
    if(packet['bytesTransferred'] > 0):
        # Check if the read packet is a configuration packet response (coming from Lycan)
        is_config = packet[0] & 0b00010000
        print('Bytes read:', packet['bytesTransferred'])
        return is_config, packet
    else:
        raise Exception('Error: No data was read from the FIFO')

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

CFGDESC = dev.getConfigurationDescriptor()
print("Configuration Descriptor")
print("\tbLength = %d" % CFGDESC.bLength)
print("\tbDescriptorType = %d" % CFGDESC.bDescriptorType)
print("\twTotalLength = %#04X (%d)" % (CFGDESC.wTotalLength, CFGDESC.wTotalLength))
print("\tbNumInterfaces = %#02X" % CFGDESC.bNumInterfaces)
print("\tbConfigurationValue = %#02X" % CFGDESC.bConfigurationValue)
print("\tiConfiguration = %#02X" % CFGDESC.iConfiguration)

# Get pipe info
# print(dev.getPipeInformation(1, 0).PipeType)
# print(dev.getPipeInformation(1, 0).PipeId)
# print(dev.getPipeInformation(1, 0).MaximumPacketSize)
# print(dev.getPipeInformation(1, 0).Interval)
# print('')
# print(dev.getPipeInformation(1, 1).PipeType)
# print(dev.getPipeInformation(1, 1).PipeId)
# print(dev.getPipeInformation(1, 1).MaximumPacketSize)
# print(dev.getPipeInformation(1, 1).Interval)

for i in range(CFGDESC.bNumInterfaces):
    IFDESC = dev.getInterfaceDescriptor(i)
    print("\tInterface Descriptor [%d]" % i)
    print("\t\tbLength = %d" % IFDESC.bLength)
    print("\t\tbDescriptorType = %d" % IFDESC.bDescriptorType)
    print("\t\tbInterfaceNumber = %#02X" % IFDESC.bInterfaceNumber)
    print("\t\tbAlternateSetting = %#02X" % IFDESC.bAlternateSetting)
    print("\t\tbNumEndpoints = %#02X" % IFDESC.bNumEndpoints)
    print("\t\tbInterfaceClass = %#02X" % IFDESC.bInterfaceClass)
    print("\t\tbInterfaceSubClass = %#02X" % IFDESC.bInterfaceSubClass)
    print("\t\tbInterfaceProtocol = %#02X" % IFDESC.bInterfaceProtocol)
    print("\t\tiInterface = %#02X" % IFDESC.iInterface)
    print("")
    for j in range(IFDESC.bNumEndpoints):
            PIPEIF = dev.getPipeInformation(i, j)
            print("\t\tPipe Information [%d]" % j)
            print("\t\t\tPipeType = %d" % PIPEIF.PipeType)
            print("\t\t\tPipeId = %#02X" % PIPEIF.PipeId)
            print("\t\t\tMaximumPacketSize = %#02X" % PIPEIF.MaximumPacketSize)
            print("\t\t\tInterval = %#02X" % PIPEIF.Interval)
            print("")

# Try to send data to the FIFO
numBytesWritten = 0
numBytesWritten += dev.writePipe(0x02, b'ABCD', 4)
print(f'Total number of bytes written: {numBytesWritten}')