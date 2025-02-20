#pragma once
#ifndef LYCANWINDOW_H
#define LYCANWINDOW_H

#include <QTabWidget>
#include <QWidget>
#include <QPushButton>
#include <QTextEdit>
#include <QCheckBox>
#include <QLineEdit>
#include <QComboBox>
#include <QHBoxLayout>
#include <QFormLayout>
#include "lycan.h"
#include <mutex>
#include <iostream>
#include <fstream>
#include <ctime>
#include <cmath>
#include <thread>
#include <functional>
#include "peripheraltab.h"

class PeripheralTab;

QT_BEGIN_NAMESPACE
namespace Ui {
class LycanWindow;
}
QT_END_NAMESPACE

class LycanWindow : public QTabWidget
{
    Q_OBJECT

public:
    Lycan* dev;
    std::mutex* mut;
    std::thread* rxThread;
    PeripheralTab* tabs[8];
    LycanWindow(QWidget *parent = nullptr);
    ~LycanWindow();
    int writeToFifo(unsigned int periphIndex, std::vector<u_char> data);
    void readFromFifo();

private:
    Ui::LycanWindow *ui;
};
#endif // LYCANWINDOW_H
