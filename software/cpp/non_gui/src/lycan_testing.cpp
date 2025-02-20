#include "lycan.h"
#include <iostream>
#include <iomanip>
#include <thread>
#include <mutex>

int main() {
    Lycan* l = new Lycan();
    int numWrote = l->writeRawBytes({0x0F, 'H', 'I', '!'});
    std::cout << "Wrote " << numWrote << " bytes" << std::endl;
    std::vector<u_char> v = l->readRawBytes(4);
    std::cout << std::string(v.begin(), v.end()) << std::endl;
}