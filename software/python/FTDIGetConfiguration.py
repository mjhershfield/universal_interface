import ftd3xx
from ftd3xx.defines import *

numDevices = ftd3xx.createDeviceInfoList()
devices = ftd3xx.getDeviceInfoList()
# # print('Number of devices: ', numDevices)

# # Pick the first device in the list (for now)
if(devices != None):
    # Create a ftd3xx device instance
    dev = ftd3xx.create(devices[0].SerialNumber, FT_OPEN_BY_SERIAL_NUMBER)
    devInfo = dev.getDeviceInfo()
    dev.setPipeTimeout(0x02, 3000)
    dev.setPipeTimeout(0x82, 3000)
    # Print some info about the device
    # print('Device Info:')
    # print(f'Type: {devInfo["Type"]}')
    # print(f'ID: {devInfo["ID"]}')
    # print(f'Descr.: {devInfo["Description"]}')
    # print(f'Serial Num: {devInfo["Serial"]}')
else:
    raise Exception('Error: No devices detected. Exiting...')

chipCfg = dev.getChipConfiguration()
print(chipCfg.OptionalFeatureSupport)

dev.close()