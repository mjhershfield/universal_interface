import PyD3XX


class Lycan():

    # Lycan object constructor
    def __init__(self):
        # Set up FTDI module and device
        PyD3XX.SetPrintLevel(PyD3XX.PRINT_ALL) # Make PyD3XX not print anything.
        Status, DeviceCount = PyD3XX.FT_CreateDeviceInfoList() # Create a device info list.
        self.connectedFtdiCount = DeviceCount
        if Status != PyD3XX.FT_OK:
            raise Exception(PyD3XX.FT_STATUS_STR[Status] + ' | FAILED TO CREATE DEVICE INFO LIST: ABORTING')
        if (DeviceCount == 0):
            raise Exception('NO DEVICES DETECTED: ABORTING')
        Status, Device = PyD3XX.FT_GetDeviceInfoDetail(0) # Get info of a device at index 0.
        if Status != PyD3XX.FT_OK:
            raise Exception(PyD3XX.FT_STATUS_STR[Status] + ' | FAILED TO GET INFO FOR DEVICE 0')
        Status = PyD3XX.FT_Create(0, PyD3XX.FT_OPEN_BY_INDEX, Device) # Open the device we're using.
        if Status != PyD3XX.FT_OK:
            raise Exception(PyD3XX.FT_STATUS_STR[Status] + ' | FAILED TO OPEN DEVICE: ABORTING')
        Status, ReadPipeCH1 = PyD3XX.FT_GetPipeInformation(Device, 1, 1)
        if Status != PyD3XX.FT_OK:
            raise Exception(PyD3XX.FT_STATUS_STR[Status] + ' | FAILED TO GET CH 1:1 INFO')
        Status, WritePipeCH1 = PyD3XX.FT_GetPipeInformation(Device, 1, 0)
        if Status != PyD3XX.FT_OK:
            raise Exception(PyD3XX.FT_STATUS_STR[Status] + ' | FAILED TO GET CH 1:0 INFO')
        self.inPipe = ReadPipeCH1
        self.outPipe = WritePipeCH1
        self.ftdiDev = Device
        PyD3XX.FT_SetPipeTimeout(Device, self.inPipe, 500)
        PyD3XX.FT_SetPipeTimeout(Device, self.outPipe, 500)
        PyD3XX.FT_SetSuspendTimeout(Device, 0)
        print('Flushing...')
        self.flush_in_pipe()
        print("Device (index, serial, desc): 0, " + Device.SerialNumber + ", " + Device.Description)

    def flush_in_pipe(self):
        # Flush the in pipe
        try:
            PyD3XX.FT_AbortPipe(self.ftdiDev, self.inPipe)
        except Exception as e:
            print(e)
            pass

    def read_raw_bytes(self, length=4):
        # Read data from specified pipe
        status, readBuff, numBytesRead = PyD3XX.FT_ReadPipe(self.ftdiDev, self.inPipe, length, 0)
        if(status != PyD3XX.FT_OK):
            raise Exception(f'Error with reading. Status Code {status}')
        elif(numBytesRead != length):
            raise Exception(f'Error with reading. Tried to read {length} bytes, but only read {numBytesRead}.')
        readVal = readBuff.Value()
        return numBytesRead, readVal
    
    def read_packet(self):
        bytesRead, readVal = self.read_raw_bytes(length=4)
        if(bytesRead > 0):
            # Check if the read packet is a configuration packet response (coming from Lycan)
            is_config = readVal[3] & 0b00010000
            periphAddr = (readVal[3] & 0b11100000) >> 5
            validBytes = (readVal[3] * 0b00001100) >> 2
            data = readVal[0:validBytes]
            print('Bytes read:', hex(int.from_bytes(readVal, 'little')))
            return is_config, periphAddr, data
        else:
            return False, -1, None
        
    def interpret_raw_bytes(self, raw):
        is_config_arr = []
        periphAddr_arr = []
        data_arr = []
        while(len(raw) >= 4):
            # For each packet
            packet = raw[0:4]
            # Check if the read packet is a configuration packet response (coming from Lycan)
            is_config = (raw[3] & 0b00010000) >> 4
            is_config_arr += [is_config]
            periphAddr = (raw[3] & 0b11100000) >> 5
            periphAddr_arr += [periphAddr]
            if(is_config):
                config_write = (raw[3] & 0b00001000) >> 3
                if(not config_write):
                    print('Received Config Packet...')
                    addr = (raw[3] & 0b00000111) # Address
                    val = raw[0:3]
                    data_arr += [addr.to_bytes(1, 'little') + val]
                else:
                    print('Ignoring Config \'Write\' Packet')
            else:
                data_arr += [raw[0:3]]
            # Move on to next packet
            raw = raw[4:]
        return is_config_arr, periphAddr_arr, data_arr

    def construct_data_packet(self, peripheral_addr, data):
        # Check that data is 3 bytes or less
        datalen = len(data)
        if(datalen > 3):
            raise Exception('Error: Too many data bytes for one packet (> 3)')
        elif(datalen < 3):
            # Pad data with 0s
            for i in range(3 - len(data)):
                data += b'\x00'
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
    
    def write_raw_bytes(self, raw):
        # write data to specified pipe	
        writeBuff = PyD3XX.FT_Buffer.from_bytes(raw)
        status, numBytesTransferred = PyD3XX.FT_WritePipe(self.ftdiDev, self.outPipe, writeBuff, len(raw), 0)
        if(status != PyD3XX.FT_OK):
            raise Exception(f'Error with writing. Status Code {status}')
        elif(numBytesTransferred != len(raw)):
            raise Exception(f'Error with writing. Tried to write {len(raw)} bytes, but only wrote {numBytesTransferred}.')
        return numBytesTransferred

    def write_data(self, peripheral_addr, data):
        # For every 3 bytes of data, send a packet
        numBytesWritten = 0
        while(len(data) > 0):
            packet = self.construct_data_packet(peripheral_addr, data[0:3])
            print('Packet to be transmitted: ', packet)
            numBytesWritten += self.write_raw_bytes(raw=packet)
            data = data[3:]
        return numBytesWritten

    def write_config_command(self, peripheral_addr=0, write=True, reg_addr=0, reg_val=0):
        # Check that the peripheral address is within the correct range
        if(peripheral_addr < 0 or peripheral_addr > 7):
            raise Exception('Error: The peripheral address is out of range (0 to 7)')
        # Check that register address is 3 bits
        if(reg_addr < 0 or reg_addr > 7):
            raise Exception('Error: Register address invalid (must be 0-7)')
        # Check that register value is 3 bytes max
        if(reg_val < 0 or reg_val > 16777215):
            raise Exception('Error: Invalid register value (max of 24 bits)')
        # Construct the packet
        packet = peripheral_addr << 32 - 3 # address
        packet += 1 << 29 - 1 # config flag bit
        packet += write << 28 - 1 # read/write bit
        packet += reg_addr << 27 - 2
        packet += reg_val
        # Transmit the packet
        print('Packet to be transmitted: ', packet.to_bytes(4, 'little'))
        numBytesTransferred = self.write_raw_bytes(packet.to_bytes(4, 'little'))
        return numBytesTransferred

    def close(self):
        print('Closing device')
        status = PyD3XX.FT_Close(self.ftdiDev)
        if(status != PyD3XX.FT_OK):
            print(f'Error closing device. Status Code {status}')
        return