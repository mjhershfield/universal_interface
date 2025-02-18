#include "lycanwindow.h"
#include <QString>
#include <windows.h>

LycanWindow::LycanWindow(QWidget *parent) : QTabWidget(parent)
{
    setWindowTitle("Lycan Universal Interface");
    setGeometry(200, 200, 960, 540);

    // Initialize Lycan device object
    dev = new Lycan();
    // dev = nullptr;

    // Initialize mutex
    mut = new std::mutex();

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
    mut->lock();
    int res = dev->writeData(periphIndex, data);
    mut->unlock();

    return res;
}

void LycanWindow::readFromFifo() {
    while(true) {
        mut->lock();
        Lycan::ReadResult res = dev->readPacket();
        mut->unlock();
        unsigned int pId = res.peripheralAddr;
        if(!res.rawPacket.empty() && tabs[pId] != nullptr) {
            tabs[pId]->displayRXData(res.data);
        }
        Sleep(100);
    }
}
