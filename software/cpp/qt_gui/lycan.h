#include "FTD3XX.h"
#include <vector>
#include <string>

// This is the Lycan Driver header file //

class Lycan {

public:

    struct ReadResult {
        std::vector<u_char> rawPacket;
        std::vector<u_char> data;
        u_int peripheralAddr;
        bool isConfig;
    };

    FT_HANDLE dev = NULL;

    // Constructor
    Lycan();

    // Method to send raw bytes to Lycan
    int writeRawBytes(std::vector<u_char> raw);

    // Method to read raw bytes from Lycan
    std::vector<u_char> readRawBytes(const u_int length);

    // Method to construct Lycan data packet
    std::vector<u_char> constructDataPacket(u_int peripheralAddr, std::vector<u_char> data);

    // Method to write a Lycan data packet to the device
    int writeDataPacket(u_int peripheralAddr, std::vector<u_char> data);

    // Method to write multiple Lycan data packets, given data
    int writeData(u_int peripheralAddr, std::vector<u_char> data);

    // Method to read a Lycan packet (data or config)
    ReadResult readPacket();

};
