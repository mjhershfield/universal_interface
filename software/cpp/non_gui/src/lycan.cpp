#include "lycan.h"
#include <stdexcept>

// This is the Lycan Driver source file //

// Class constructor
Lycan::Lycan() {
    FT_STATUS ftStatus = FT_OK;
    ftStatus = FT_Create(0, FT_OPEN_BY_INDEX, &dev); // Open the first device
    if(FT_FAILED(ftStatus)) {
        throw std::runtime_error("Error creating device!");
    }
}

// Method to write raw bytes
int Lycan::writeRawBytes(std::vector<u_char> raw) {
    FT_STATUS ftStatus = FT_OK;
    ULONG ulBytesWritten = 0;
    PUCHAR pucBuffer = new UCHAR[raw.size()]; // allocate memory
    int length = raw.size();
    std::copy(raw.begin(), raw.end(), pucBuffer);
    ftStatus = FT_WritePipe(dev, 0x02, pucBuffer, raw.size(), &ulBytesWritten, NULL);
    delete[] pucBuffer; // release memory
    if(FT_FAILED(ftStatus)) {
        return -1;
    }
    return (int)ulBytesWritten;
}

// Method to read raw bytes
std::vector<u_char> Lycan::readRawBytes(const u_int length) {
    FT_STATUS ftStatus = FT_OK;
    ULONG ulBytesRead = 0;
    PUCHAR pucBuffer = new UCHAR[length]; // allocate memory
    ftStatus = FT_ReadPipe(dev, 0x82, pucBuffer, length, &ulBytesRead, NULL);
    if(!FT_FAILED(ftStatus) && ulBytesRead > 0) {
        std::vector<u_char> raw(ulBytesRead);
        std::copy(pucBuffer, pucBuffer + ulBytesRead, raw.begin());
        delete[] pucBuffer; // release memory
        return raw;
    } else {
        delete[] pucBuffer; // release memory
        return {};
    }
}

// Method to construct a Lycan data packet
std::vector<u_char> Lycan::constructDataPacket(u_int peripheralAddr, std::vector<u_char> data) {
    // Check that the data length is 3 bytes or less, but not 0
    if(data.size() > 3 || data.size() == 0) {
        return {};
    }
    // Check peripheral address
    if(peripheralAddr < 0 || peripheralAddr > 7) {
        return {};
    }
    // Convert the data bytes to an integer number
    int32_t i32Data = 0;
    for(unsigned int i = 0; i < data.size(); i++) {
        i32Data += data[i] << 8*(i);
    }
    // Construct the packet
    int32_t i32Packet = 0;
    i32Packet += (peripheralAddr << 32-3); // peripheral address
    i32Packet += (0 << 32-4); // config flag
    i32Packet += (data.size() << 32-6); // num valid bytes
    i32Packet += (3 << 32-8); // don't cares
    i32Packet += i32Data;
    // Convert the packet to a vector of 4 bytes (little-endian)
    std::vector<u_char> packet(4);
    for(u_int i = 0; i < 4; i++) {
        packet[i] = (i32Packet & (0xFF << (i*8))) >> i*8;
    }
    return packet;
}

// Method to write a Lycan data packet to the device
int Lycan::writeDataPacket(u_int peripheralAddr, std::vector<u_char> data) {
    std::vector<u_char> packet = constructDataPacket(peripheralAddr, data);
    return writeRawBytes(packet);
}

// Method to write multiple Lycan data packets, given data
int Lycan::writeData(u_int peripheralAddr, std::vector<u_char> data) {
    int numBytesWritten = 0;
    // Continue until data is used up
    while(data.size() >= 3) {
        std::vector<u_char> d(data.begin(), data.begin() + 3); // get the first 3 bytes of data
        numBytesWritten += writeDataPacket(peripheralAddr, d);
        data.erase(data.begin(), data.begin() + 3); // remove the first 3 bytes of data
    }
    if(data.size() > 0) {
        // Write one more data packet
        numBytesWritten += writeDataPacket(peripheralAddr, data);
    }
    return numBytesWritten;
}

// Method to synchronously read a Lycan packet (data or config)
Lycan::ReadResult Lycan::readPacket() {
    std::vector<u_char> rawPacket = readRawBytes(4); // read
    if(rawPacket.size() == 4) {
        u_int peripheralAddr = (rawPacket[3] & 0b11100000) >> 5; // parse out peripheral address
        bool isConfig = (rawPacket[3] & 0b00010000) >> 4; // parse out config flag
        std::vector<u_char> data((rawPacket[3] & 0b00001100) >> 2); // parse out valid bytes flag
        // Parse out the data byte values (for numValidBytes)
        for(int i = 0; i < data.size(); i++) {
            data[i] = rawPacket[i];
        }
        Lycan::ReadResult res = {rawPacket, data, peripheralAddr, isConfig};
        return res;
    } else {
        Lycan::ReadResult res = {{}, {}, 0, false};
        throw std::runtime_error("Error reading a packet!");
        return res;
    }
}