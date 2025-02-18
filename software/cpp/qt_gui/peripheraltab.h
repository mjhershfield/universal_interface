#ifndef PERIPHERALTAB_H
#define PERIPHERALTAB_H
#pragma once
#include "lycanwindow.h"

class LycanWindow;

class PeripheralTab : public QWidget
{
    Q_OBJECT
public:

    LycanWindow* parentWindow;

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

    explicit PeripheralTab(unsigned int periphIndex, LycanWindow *parent = nullptr);
    void initComponents();
    void createLogFile();
    void onSubmitTX();
    void displayRXData(std::vector<u_char> data);

signals:
};

#endif // PERIPHERALTAB_H
