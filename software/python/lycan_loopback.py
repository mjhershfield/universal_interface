import argparse
import lycan
import random

def main(loopCount):
    lycanDev = lycan.Lycan()

    successCount = 0
    pId = 0
    for run in range(loopCount):
        # Try to send data to the FIFO
        data = random.getrandbits(24).to_bytes(3, 'little')
        pId = random.randrange(8)
        lycanDev.write_data(peripheral_addr=pId, data=data)
        isConfig, periphAddr, readData = lycanDev.read_packet()

        # Compare write/read data
        if(readData != None and data == readData and pId == periphAddr):
            successCount += 1
            print('******************************   The loopback worked! Yay!   ******************************')
        else:
            print('******************************   Loopback Failed :(   ******************************')
    
    print(f'\n\n\n**********\tNumber of successes: {successCount}\t({(successCount/loopCount)*100}%)\t**********\n')

    key = input('\n\nPress any key to exit...')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="data loopback demo application")
    parser.add_argument('-l', '--loop_count', type=int, default=10000, help="number of tests to run (default is 10000)")
    args = parser.parse_args()
    main(args.loop_count)