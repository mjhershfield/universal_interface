#include "peripheraltab.h"

int32_t dataStringToNum(std::string inStr, std::string format) {
    int32_t res = 0;
    // Check format of input string
    if(format.compare("Dec") == 0) {
        int32_t num = std::stoi(inStr);
        res = num;
    } else if(inStr.length() == 24 && format.compare("Bin") == 0) {
        for(unsigned int i = 0; i < inStr.length(); i++) {
            res += pow(2, (23 - i)) * ((int)inStr[i] - 48);
        }
    } else { // string is in decimal format
        if(inStr.length() != 6) {
            res = -1;
        }
        for(unsigned int i = 0; i < inStr.length(); i++) {
            if(std::isdigit(inStr[i]) || ('a' <= std::tolower(inStr[i]) && std::tolower(inStr[i]) <= 'f')) {
                if(std::isdigit(inStr[i])) {
                    res += pow(16, 5-i) * ((int)inStr[i] - 48);
                } else {
                    res += pow(16, 5-i) * ((int)std::tolower(inStr[i]) - 87);
                }
            } else {
                res = -1;
            }
        }
    }
    return res;
}

PeripheralTab::PeripheralTab(Lycan* dev, std::mutex* mut, unsigned int periphIndex, QWidget *parent)
    : QWidget{parent}
{
    this->lycanDev = dev;
    this->mut = mut;
    this->periphIndex = periphIndex;
    initComponents();
}

void PeripheralTab::createLogFile() {
    if(!logging) {
        try {
            logFileName = "p_" + std::to_string(periphIndex) + "_log_" + std::to_string(std::time(nullptr)) + ".txt";
            logFile.open(logFileName);
            logging = true;
            logButton->setStyleSheet("background-color: red;");
            logButton->setText("Stop Logging to File");
        } catch(std::runtime_error e) {
            errorLabel->setText("Error creating the log file!");
        }
    } else {
        // Save and close the logFile
        try {
            std::string msg = "Log data saved to file: " + logFileName;
            rxDataLabel->append(QString::fromStdString(msg));
            logFile.close();
            logButton->setStyleSheet("background-color: green;");
            logButton->setText("Start Logging to File");
        } catch(std::runtime_error e) {
            errorLabel->setText("Error saving/closing the log file!");
        }
    }
}

void PeripheralTab::onSubmitTX() {
    std::vector<u_char> data;
    if(txTypeCombo->currentText() != "Str") {
        int32_t dataNum = dataStringToNum(txDataField->text().toStdString(), txTypeCombo->currentText().toStdString());
        if(dataNum != -1) {
            // Convert the data integer to a vector of 4 bytes (little-endian)
            for(unsigned int i = 0; i < 4; i++) {
                data.push_back((dataNum & (0xFF << (i*8))) >> i*8);
            }
        } else {
            // Error constructing packet
            errorLabel->setText("Error constructing packet!");
            return;
        }
    } else {
        // Create a data vector using the input string
        std::vector<u_char> data;
        for(u_char c : txDataField->text().toStdString()) {
            data.insert(data.begin(), c);
        }
    }
    // Acquire mutex lock
    mut->lock();
    // Transmit data
    lycanDev->writeData(periphIndex, data);
    // Release mutex lock
    mut->unlock();
}

void PeripheralTab::initComponents() {

    logButton = new QPushButton("Start Logging to File", this);
    logButton->setStyleSheet("background-color: green;");
    logButton->setFixedWidth(120);
    connect(logButton, &QPushButton::clicked, this, &PeripheralTab::createLogFile);

    rxDataLabel = new QTextEdit(this);
    rxDataLabel->setReadOnly(true);

    configCheckbox = new QCheckBox("Config Pkt?", this);
    configCheckbox->setLayoutDirection(Qt::RightToLeft);
    configCheckbox->setCheckState(Qt::CheckState::Checked);

    txDataField = new QLineEdit(this);
    connect(txDataField, &QLineEdit::returnPressed, this, &PeripheralTab::onSubmitTX);
    txTypeCombo = new QComboBox(this);
    txTypeCombo->addItems({"Str", "Hex", "Bin", "Dec"});
    txSubmitButton = new QPushButton("Send", this);
    connect(txSubmitButton, &QPushButton::clicked, this, &PeripheralTab::onSubmitTX);

    errorLabel = new QTextEdit(this);
    errorLabel->setReadOnly(true);
    errorLabel->setFixedHeight(100);
    errorLabel->setTextColor(QColor(0xFF0000));

    // Layout Setup
    txConfigRowLayout = new QHBoxLayout();
    txConfigRowLayout->addWidget(configCheckbox, Qt::AlignmentFlag::AlignRight);
    txConfigRowLayout->setSpacing(10);

    txRowLayout = new QHBoxLayout();
    txRowLayout->addWidget(txDataField);
    txRowLayout->addWidget(txTypeCombo);
    txRowLayout->addWidget(txSubmitButton);

    layout = new QFormLayout();
    layout->addRow(logButton);
    layout->addRow("RX Data:", rxDataLabel);
    layout->addRow("", txConfigRowLayout);
    layout->addRow("TX Data:", txRowLayout);
    layout->addRow("Errors:", errorLabel);
    layout->setVerticalSpacing(10);
    setLayout(layout);

}
