#include "lycanwindow.h"
#include <QString>
#include <windows.h>

LycanWindow::LycanWindow(QWidget *parent) : QTabWidget(parent)
{
    setWindowTitle("Lycan Universal Interface");
    setGeometry(200, 200, 960, 540);

    // Initialize Lycan device object
    dev = new Lycan();
    std::cout << dev->setLycanPipeTimeout(0x82, 100) << std::endl;
    std::cout << dev->setLycanPipeTimeout(0x02, 100) << std::endl;
    // dev = nullptr;

    // Tab Setup
    for(unsigned int i = 0; i < 8; i++) {
        tabs[i] = new PeripheralTab(i, this);
        std::string tabName = "Peripheral " + std::to_string(i);
        addTab(tabs[i], QString::fromStdString(tabName));
    }

    // Initialize/start read thread
    rxThread = new std::thread(&LycanWindow::readFromFifo, this);

}

LycanWindow::~LycanWindow()
{

}

int LycanWindow::writeToFifo(unsigned int periphIndex, std::vector<u_char> data) {
    std::unique_lock<std::mutex> lock(mut); // Auto locks on creation and unlocks on out-of-scope
    int res = dev->writeData(periphIndex, data);
    return res;
}

void LycanWindow::readFromFifo() {
    while(true) {
        std::unique_lock<std::mutex> lock(mut); // Auto locks on creation
        Lycan::ReadResult res = dev->readPacket();
        lock.unlock(); // Manual unlock
        // unsigned int pId = res.peripheralAddr;
        // if(!res.rawPacket.empty() && tabs[pId] != nullptr) {
        //     tabs[pId]->displayRXData(res.data);
        // }
        Sleep(100);
    }
}
