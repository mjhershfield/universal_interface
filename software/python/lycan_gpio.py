import lycan
import time

lycanDev = lycan.Lycan()

while(True):

    isConfig, periphAddr, data = lycanDev.read_packet()

    print(f'Peripheral {periphAddr} read data: {data}')

    time.sleep(1)




