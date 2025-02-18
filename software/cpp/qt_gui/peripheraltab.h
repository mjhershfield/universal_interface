#ifndef PERIPHERALTAB_H
#define PERIPHERALTAB_H

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

class PeripheralTab : public QWidget
{
    Q_OBJECT
public:

    Lycan* lycanDev;
    std::mutex* mut;

    unsigned int periphIndex;

    QPushButton* logButton;
    QTextEdit* rxDataLabel;
    QCheckBox* configCheckbox;
    QLineEdit* txDataField;
    QComboBox* txTypeCombo;
    QPushButton* txSubmitButton;
    QTextEdit* errorLabel;
    QHBoxLayout* txConfigRowLayout;
    QHBoxLayout* txRowLayout;
    QFormLayout* layout;

    std::ofstream logFile;
    std::string logFileName;
    bool logging = false;

    explicit PeripheralTab(Lycan* dev, std::mutex* mut, unsigned int periphIndex, QWidget *parent = nullptr);
    void initComponents();
    void createLogFile();
    void onSubmitTX();

signals:
};

#endif // PERIPHERALTAB_H
