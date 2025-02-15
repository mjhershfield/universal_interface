#include "lycan.h"
#include <iostream>
#include <iomanip>
#include <thread>
#include <mutex>

typedef struct _USER_CONTEXT
{
    CRITICAL_SECTION                    m_hCriticalSection;
    HANDLE                              m_hEventDataAvailable;
    FT_NOTIFICATION_CALLBACK_INFO_DATA  m_tNotificationData;

} USER_CONTEXT, *PUSER_CONTEXT;

static VOID NotificationCallback(PVOID pvCallbackContext, E_FT_NOTIFICATION_CALLBACK_TYPE eCallbackType, PVOID pvCallbackInfo);

int main() {

    Lycan lycan; // create a lycan object

    USER_CONTEXT UserContext = {0};
    UCHAR acWriteBuf[8] = {0x11, 0x22, 0x33, 0x44, 0x00, 0xFF, 0xCC, 0x55};
    UCHAR acReadBuf[8] = {0, 0, 0, 0, 0, 0, 0, 0};

    // Get the chip configuration
    FT_STATUS ftStatus = FT_OK;
    FT_60XCONFIGURATION config = {0};
    ftStatus = FT_GetChipConfiguration(lycan.dev, &config);
    if(FT_FAILED(ftStatus)) {
        FT_Close(lycan.dev);
        std::cout << "Error getting chip config!" << std::endl;
        goto exit;
    }

    // Update the config
    config.OptionalFeatureSupport |= CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCHALL;
    ftStatus = FT_SetChipConfiguration(lycan.dev, &config);
    if(FT_FAILED(ftStatus)) {
        FT_Close(lycan.dev);
        std::cout << "Error setting chip config!" << std::endl;
        goto exit;
    }

    // Restart the device
    FT_Close(lycan.dev);
    Sleep(5000);

    // Re-open the device
    lycan = Lycan();

    // Create the event
    UserContext.m_hEventDataAvailable = CreateEvent(NULL, FALSE, FALSE, NULL);
    if(!UserContext.m_hEventDataAvailable) {
        std::cout << "Error creating the event!" << std::endl;
        goto exit;
    }

    // Initialize the critical section
    InitializeCriticalSection(&UserContext.m_hCriticalSection);

    // Set/register the callback function
    ftStatus = FT_SetNotificationCallback(lycan.dev, NotificationCallback, &UserContext);
    if(FT_FAILED(ftStatus)) {
        std::cout << "Error registering the callback!" << std::endl;
        goto exit;
    }

    {
            
        // Write data sychronously
        ULONG ulBytesTransferred = 0;
        // ftStatus = FT_WritePipe(lycan.dev, 0x02, acWriteBuf, sizeof(acWriteBuf), &ulBytesTransferred, NULL);
        // if(FT_FAILED(ftStatus)) {
        //     std::cout << "Error writing to device!" << std::endl;
        //     goto exit;
        // }
        lycan.writeDataPacket(0, {0x11, 0x22, 0x33}); // Packet: 0x0F 0x33 0x22 0x11
        lycan.writeDataPacket(1, {0xFF, 0xCC, 0x55}); // Packet: 0x2F 0x55 0xCC 0xFF
        lycan.writeDataPacket(2, {0x11, 0x22, 0x33}); // Packet: 0x0F 0x33 0x22 0x11
        // lycan.writeDataPacket(3, {0xFF, 0xCC, 0x55}); // Packet: 0x2F 0x55 0xCC 0xFF
        // lycan.writeDataPacket(4, {0x11, 0x22, 0x33}); // Packet: 0x0F 0x33 0x22 0x11
        // lycan.writeDataPacket(5, {0xFF, 0xCC, 0x55}); // Packet: 0x2F 0x55 0xCC 0xFF

        // Read data using the notification callback   
        ULONG ulCurrentRecvData = 0;
        do {
            DWORD dwRet = WaitForSingleObject(UserContext.m_hEventDataAvailable, INFINITE);
            EnterCriticalSection(&UserContext.m_hCriticalSection);
            switch (dwRet) {
                case WAIT_OBJECT_0: // Event was set by the notification callback
                {
                    if(UserContext.m_tNotificationData.ulRecvNotificationLength == 0 || UserContext.m_tNotificationData.ucEndpointNo == 0) {
                        LeaveCriticalSection(&UserContext.m_hCriticalSection);
                        std::cout << "Leaving critical section on failure" << std::endl;
                        goto exit;
                    }

                    ULONG ulBytesTransferred = 0;
                    // ftStatus = FT_ReadPipe( lycan.dev, 
                    //                         UserContext.m_tNotificationData.ucEndpointNo, 
                    //                         &acReadBuf[ulCurrentRecvData],
                    //                         UserContext.m_tNotificationData.ulRecvNotificationLength, 
                    //                         &ulBytesTransferred, 
                    //                         NULL );
                    Lycan::ReadResult res;
                    try {
                        res = lycan.readPacket();
                    } catch(const std::runtime_error &e) {
                        std::cout << e.what() << std::endl;
                    }
                    ulBytesTransferred = 4;
                    if(!FT_FAILED(ftStatus)) {
                        ulCurrentRecvData += ulBytesTransferred;
                        std::cout << "Read " << ulBytesTransferred << " bytes" << std::endl;
                    }
                    // Verify if data written is same as data read
                    UserContext.m_tNotificationData.ulRecvNotificationLength = 0;
                    UserContext.m_tNotificationData.ucEndpointNo = 0;
                    LeaveCriticalSection(&UserContext.m_hCriticalSection);
                    std::cout << "Leaving critical section on success" << std::endl;
                    // Verify if data written is same as data read
                    for(int i = 0; i < res.rawPacket.size(); i++) {
                        std::cout << std::hex << (int)res.rawPacket[i] << " ";
                    }
                    std::cout << std::endl;
                    std::cout << "Peripheral #: " << res.peripheralAddr << std::endl;
                    std::cout << "Data: " << std::endl;
                    for(int i = 0; i < res.data.size(); i++) {
                        std::cout << std::hex << (int)res.data[i] << " ";
                    }
                    std::cout << std::endl;
                    break;
                }
                default:
                {
                    LeaveCriticalSection(&UserContext.m_hCriticalSection);
                    std::cout << "Leaving critical section on DEFAULT" << std::endl;
                    break;
                }
            }
        } while (ulCurrentRecvData < 8);

    }

    exit:

        // Clear/unregister the callback function
        FT_ClearNotificationCallback(lycan.dev);

        // Delete event and critical section
        DeleteCriticalSection(&UserContext.m_hCriticalSection);
        if(UserContext.m_hEventDataAvailable) {
            CloseHandle(UserContext.m_hEventDataAvailable);
            UserContext.m_hEventDataAvailable = NULL;
        }

        // Close device handle
        FT_Close(lycan.dev);
    
    return 0;

}

// The callback function should be as minimum as possible so as not to block any activity
// In this function, as illustrated, we just copy the callback result/information and then exit the function
static VOID NotificationCallback(PVOID pvCallbackContext, E_FT_NOTIFICATION_CALLBACK_TYPE eCallbackType, PVOID pvCallbackInfo)
{
    switch (eCallbackType)
    {
        case E_FT_NOTIFICATION_CALLBACK_TYPE_DATA:
        {
            PUSER_CONTEXT pUserContext = (PUSER_CONTEXT)pvCallbackContext;
            FT_NOTIFICATION_CALLBACK_INFO_DATA* pInfo = (FT_NOTIFICATION_CALLBACK_INFO_DATA*)pvCallbackInfo;

            std::cout << "Notification callback called!" << std::endl;

            EnterCriticalSection(&pUserContext->m_hCriticalSection);
            memcpy(&pUserContext->m_tNotificationData, pInfo, sizeof(*pInfo));
            SetEvent(pUserContext->m_hEventDataAvailable);
            LeaveCriticalSection(&pUserContext->m_hCriticalSection);

            break;
        }
        case E_FT_NOTIFICATION_CALLBACK_TYPE_GPIO: // fall-through
        default:
        {
            break;
        }
    }
}