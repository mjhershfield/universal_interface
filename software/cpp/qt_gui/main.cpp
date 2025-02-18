#include "lycanwindow.h"

#include <QApplication>

int main(int argc, char *argv[])
{

    QApplication a(argc, argv);
    LycanWindow w;
    w.show();
    return a.exec();

}
