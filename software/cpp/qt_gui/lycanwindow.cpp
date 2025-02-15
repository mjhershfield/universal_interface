#include "lycanwindow.h"
#include <iostream>
#include <QString>

LycanWindow::LycanWindow(Lycan* dev, std::mutex* mut, QWidget *parent) : QTabWidget(parent)
{
    setWindowTitle("Lycan Universal Interface");
    setGeometry(200, 200, 960, 540);

    // Tab Setup
    PeripheralTab* peripheralTabs[8];
    for(unsigned int i = 0; i < 8; i++) {
        peripheralTabs[i] = new PeripheralTab(dev, mut, i);
        std::string tabName = "Peripheral " + std::to_string(i);
        addTab(peripheralTabs[i], QString::fromStdString(tabName));
        std::cout << "Added Periph Tab #{i}" << std::endl;
    }
}

LycanWindow::~LycanWindow()
{

}
