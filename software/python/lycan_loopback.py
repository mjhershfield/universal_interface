import argparse
import lycan
import random
import PyD3XX
import sys, time

def main(loopCount, pId):
    lycanDev = lycan.Lycan()

    # Check that the device is set up properly
    status, config = PyD3XX.FT_GetChipConfiguration(lycanDev.ftdiDev)
    if status != PyD3XX.FT_OK:
        print('FAILED TO READ CHIP CONFIG OF DEVICE 0: ABORTING')
        sys.exit(1)
    CH1_NotificationsEnabled = (config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1) != 0
    if CH1_NotificationsEnabled:
        print('Config included notification support, reconfiguring and cycling port')
        config.OptionalFeatureSupport = config.OptionalFeatureSupport & ~PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1
        PyD3XX.FT_SetChipConfiguration(lycanDev.ftdiDev, config)
        if status != PyD3XX.FT_OK:
            print('FAILED TO WRITE CHIP CONFIG OF DEVICE 0: ABORTING')
            sys.exit(1)
        status, config = PyD3XX.FT_GetChipConfiguration(lycanDev.ftdiDev)
        if status != PyD3XX.FT_OK:
            print('FAILED TO READ CHIP CONFIG OF DEVICE 0: ABORTING')
            sys.exit(1)
        CH1_NotificationsEnabled = (config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1) != 0
        if CH1_NotificationsEnabled:
            print('CH1 NOTIFICATIONS COULD NOT BE DISABLED: ABORTING')
            sys.exit(1)

    successCount = 0
    for run in range(loopCount):
        # Try to send data to the FIFO
        data = random.getrandbits(24).to_bytes(3, 'little')
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
    parser.add_argument('-p', '--peripheral_id', type=int, default=0, help="peripheral ID (0-7) to send/receive packets (default is 0)")
    args = parser.parse_args()
    main(args.loop_count, args.peripheral_id)