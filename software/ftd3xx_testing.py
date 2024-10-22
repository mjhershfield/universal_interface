import ftd3xx

def send_data(device, pipe=0x00, peripheral_addr=0, data=0x101011):
    # For every 3 bytes of data, send a packet
    while(len(data) >= 3):
        send_data_packet(device, pipe, data[:3], peripheral_addr)
    # Send the rest of the data
    send_data_packet(device, pipe, data, peripheral_addr)

def send_data_packet(device, pipe=0x00, peripheral_addr=0, data=0x101011):
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
    packet += data
    # Transmit the packet
    ftd3xx.writePipe(device, pipe, packet, len(packet))

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
    ftd3xx.writePipe(device, pipe, packet, len(packet))

def read_config_reg(device, pipe=0x00, peripheral_addr=0, reg_addr=0):
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
    ftd3xx.writePipe(device, pipe, packet, len(packet))


# Create a list of device info and print the number of devices
numDevices = ftd3xx.createDeviceInfoList()
devices = ftd3xx.getDeviceInfoList()
print('Number of devices: ', numDevices)

# Pick the first device in the list (for now)
if(devices != None):
    dev = devices[0]
else:
    raise Exception('Error: No devices detected. Exiting...')