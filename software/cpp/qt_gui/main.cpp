#include "lycanwindow.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    Lycan* dev = nullptr;
    std::mutex* mut = new std::mutex();

    QApplication a(argc, argv);
    LycanWindow w(dev, mut);
    w.show();
    return a.exec();
}
