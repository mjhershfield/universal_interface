import sys
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QFormLayout, 
    QPushButton, QHBoxLayout, QCheckBox, QComboBox, QTextEdit,
    QTabWidget
)
from PyQt6.QtGui import QIntValidator, QColor
import pyqtgraph as pg
import ftd3xx, threading, time, queue
from ftd3xx.defines import *
import ftd3xx_functions as ftdi
from random import randint

# Constants #

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

# Global Vars #

turn = 'R'

# Helper Functions #

# String to number (bytes) method
def str_to_num(inStr, format):
    res = 0
    # Check if the string is in binary, hex, or decimal
    if(format=='Dec'):
        num = int(inStr)

        # TODO: Check if number is invalid

        return int(inStr)
    
    elif(len(inStr) == 24 and format=='Bin'):
        for index, c in enumerate(inStr):
            res += (2**(23 - index)) * (ord(c) - 48)
        return res
    
    else: # String is in hexadecimal
        if(len(inStr) != 6):
            return -1
        for index, c in enumerate(inStr):
            if(c.isdigit() or ('a' <= c.lower() <= 'f')):
                if(c.isdigit()):
                    res += (16**(5 - index)) * (ord(c) - 48)
                else:
                    res += (16**(5 - index)) * (ord(c.lower()) - 87)
            else:
                return -1 # Not a proper hex string
        return res
    
def write_to_FIFO(dev, mutex, periphAddr, isConfig, data, format='Hex'):
    data_num = str_to_num(data, format)
    # print(data_num)
    if(data_num != -1):
        # Convert integer packet to bytes object
        data_b = data_num.to_bytes(3, 'little')
        # Write to the FIFO
        mutex.acquire() # Acquire the I/O threading lock (blocking)
        num_bytes_written = ftdi.write_data_packet(dev, peripheral_addr=periphAddr, data=data_b)
        mutex.release() # Release the threading lock
        return data_b, num_bytes_written
    else:
        return None, -1

# Thread for reading from FIFO (Pauses if writing)
def read_from_FIFO(dev, GUI, mutex):
    while(True):
        mutex.acquire() # Acquire the I/O threading lock (blocking)
        data_in = ftdi.read_packet(dev, suppressErrors=True)[1] # Read from the FIFO
        mutex.release() # Release the threading lock
        # print('Read:', data_in)
        if(data_in != None):
            # Send the read packet to the corresponding peripheral tab
            periphIndex = int.from_bytes(data_in, 'little') >> 29
            if(GUI.peripheralTabs[periphIndex]):
                data = data_in[0:3]
                GUI.peripheralTabs[periphIndex].displayRXData(str(hex(int.from_bytes(data, 'little'))), True)
        # Tell the main thread we are sleeping
        time.sleep(0.1) # Sleep for 100 ms (CHANGE LATER???)
    
# Peripheral Tab Class #
class PeripheralTab(QWidget):

    # Constructor
    def __init__(self, mutex, dev, peripheralIndex=0):
        super().__init__()

        self.mutex = mutex
        self.dev = dev
        self.pIndex = peripheralIndex
        self.logFile = 0 # No log file yet
        self.logging = False

        # self.setWindowTitle("Lycan Universal Interface")
        # self.setGeometry(200, 200, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Component Setup
    def initComponents(self): 
        self.logButton = QPushButton('Start Logging to File')
        self.logButton.setStyleSheet('background-color: green;')
        self.logButton.setFixedWidth(120)
        self.logButton.clicked.connect(self.createLogFile)
        
        self.rxDataLabel = QTextEdit()
        self.rxDataLabel.setReadOnly(True)

        self.configCheckbox = QCheckBox('Config Pkt?')
        self.configCheckbox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.configCheckbox.setCheckState(Qt.CheckState.Unchecked)

        self.txDataField = QLineEdit()
        self.txDataField.returnPressed.connect(self.onSubmitTX)
        self.txTypeCombo = QComboBox()
        self.txTypeCombo.addItems(['Hex', 'Bin', 'Dec'])
        self.txSubmitButton = QPushButton('Send')
        self.txSubmitButton.clicked.connect(self.onSubmitTX)

        self.errorLabel = QTextEdit()
        self.errorLabel.setReadOnly(True)
        self.errorLabel.setFixedHeight(100)
        self.errorLabel.setTextColor(QColor(0xFF0000))

        # Layout Setup #

        txConfigRowLayout = QHBoxLayout()
        txConfigRowLayout.addWidget(self.configCheckbox, alignment=Qt.AlignmentFlag.AlignRight)
        txConfigRowLayout.setSpacing(10)

        txRowLayout = QHBoxLayout()
        txRowLayout.addWidget(self.txDataField)
        txRowLayout.addWidget(self.txTypeCombo)
        txRowLayout.addWidget(self.txSubmitButton)

        layout = QFormLayout()
        layout.addRow(self.logButton)
        layout.addRow('RX Data:', self.rxDataLabel)
        layout.addRow('', txConfigRowLayout)
        layout.addRow('TX Data:', txRowLayout)
        layout.addRow('Errors:', self.errorLabel)
        layout.setVerticalSpacing(10)
        self.setLayout(layout)

    # On request to send to FIFO
    def onSubmitTX(self):
        res = write_to_FIFO(self.dev, self.mutex, self.pIndex, False, self.txDataField.text(), self.txTypeCombo.currentText())
        if(res[1] == -1):
            message = 'Issue with input (may have too many bytes, or formatting is wrong - use binary or hex), try again.'
            self.errorLabel.setText(message)
        elif(res[1] == 0):
            message = 'Data failed to write to FIFO!'
            self.errorLabel.setText(message)
        else:
            self.errorLabel.setText('') # Reset the error text box
            # self.txDataField.setText('') # Reset the TX field text
            self.rxDataLabel.append(f'\tWrote {res[1]} bytes to the FIFO.\n')
            self.logData(res[0], )

    def displayRXData(self, data):
        self.rxDataLabel.append('Read: '+data+'\n')
        self.logData(data, True)

    def createLogFile(self):
        if(not self.logging):
            try:
                self.logFile = open(f'p_{self.pIndex}_log_{str(int(time.time()))}.txt', 'w')
                self.logging = True
                self.logButton.setStyleSheet('background-color: red;')
                self.logButton.setText('Stop Logging to File')
            except Exception as e:
                print(e)
                self.errorLabel.setText('Error creating the log file!')
        else:
            # Close the log file (and save it)
            try:
                self.rxDataLabel.append('Log data saved to file: ' + self.logFile.name + '\n')
                self.logFile.close()
                self.logging = False
                self.logButton.setStyleSheet('background-color: green;')
                self.logButton.setText('Start Logging to File')
            except Exception as e:
                print(e)
                self.errorLabel.setText('Error saving/closing the log file!')

    def logData(self, data, isRX):
        timestamp = str(time.time())
        if(self.logging):
            try:
                if(isRX):
                    self.logFile.write(f'{timestamp}:\t{str(data)}\n')
            except Exception as e:
                print(e)
                self.errorLabel.setText('Error writing to log file!')

# Main Window Class #
class LycanWindow(QTabWidget):

    # Constructor
    def __init__(self, threadQueue, dev, numPeripherals):
        super().__init__()

        self.threadQueue = threadQueue
        self.dev = dev

        self.setWindowTitle("Lycan Universal Interface")
        self.setGeometry(200, 200, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Tab Setup #
        self.peripheralTabs = [0]*numPeripherals
        for i in range(0, numPeripherals):
            self.peripheralTabs[i] = PeripheralTab(threadQueue, dev, i)
            self.peripheralTabs[i].initComponents()
            self.addTab(self.peripheralTabs[i], f'Peripheral {i}')
            print(f'Added Periph Tab #{i}')

        # Show the GUI
        self.show()

    def closeEvent(self, event):
        self.dev.close()


# Main #
if __name__ == '__main__':

    # Create a queue for message passing between main thread and RX thread
    threadQueue = queue.Queue(maxsize=1)
    threadQueue.put(True)

    # Get the connected FTDI device
    numDevices = ftd3xx.createDeviceInfoList()
    devices = ftd3xx.getDeviceInfoList()
    if(devices != None):
        # Create a ftd3xx device instance
        dev = ftd3xx.create(devices[0].SerialNumber, FT_OPEN_BY_SERIAL_NUMBER)
        devInfo = dev.getDeviceInfo()
        dev.setPipeTimeout(0x02, 500)
        dev.setPipeTimeout(0x82, 500)
        dev.setSuspendTimeout(0)
        # Print some info about the device
        print('\nDevice Info:')
        print(f'\tType: {devInfo["Type"]}')
        print(f'\tID: {devInfo["ID"]}')
        print(f'\tDescr.: {devInfo["Description"]}')
        print(f'\tSerial Num: {devInfo["Serial"]}')
    else:
        message = 'Error: No devices detected. Exiting...'
        sys.exit()

    mutex = threading.Lock()

    app = QApplication(sys.argv)
    gui = LycanWindow(mutex, dev, 8)

    read_t = threading.Thread(target=read_from_FIFO, args=(dev, gui, mutex), daemon=True)

    # Start the reading thread
    read_t.start()

    sys.exit(app.exec())