import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QFormLayout, 
    QPushButton, QHBoxLayout, QCheckBox, QComboBox, QTextEdit,
    QTabWidget
)
from PyQt6.QtGui import QIntValidator, QColor
import ftd3xx, threading, time, queue
from ftd3xx.defines import *
import ftd3xx_functions as ftdi
import random, socket

# Constants #

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

# Global Vars #

turn = 'R'

# Helper Functions #

# String to number (bytes) method
def str_to_num(inStr, isHex):
    res = 0
    # Check if the string is in binary
    if(len(inStr) == 24 and not isHex):
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
    
def write_to_FIFO(dev, mutex, periphAddr, isConfig, data, isHex):
    data_num = str_to_num(data, isHex)
    print(data_num)
    if(data_num != -1):
        # Convert integer packet to bytes object
        data_clean = data_num.to_bytes(3, 'little')
        # Write to the FIFO
        mutex.acquire() # Acquire the I/O threading lock (blocking)
        # DO NOTHING
        mutex.release() # Release the threading lock
        return data_clean, 4
    else:
        return None, -1

# Thread for reading from FIFO (Pauses if writing)
def read_from_FIFO(dev, GUI, mutex):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 5000
    client_socket.connect((host, port))

    while True:
        mutex.acquire() # Acquire the I/O threading lock (blocking)
        data_in = client_socket.recv(4) # Simulated FIFO read (over port 5000)
        mutex.release() # Release the threading lock
        if(len(data_in) > 0):
            # Send the read packet to the corresponding peripheral tab
            periphIndex = int.from_bytes(data_in, 'little') >> 29
            if(GUI.peripheralTabs[periphIndex]):
                data = data_in[0:3]
                GUI.peripheralTabs[periphIndex].displayRXData(str(hex(int.from_bytes(data, 'little'))))
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

        # self.setWindowTitle("Lycan Universal Interface")
        # self.setGeometry(200, 200, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Component Setup #

        self.rxDataLabel = QTextEdit()
        self.rxDataLabel.setReadOnly(True)

        self.configCheckbox = QCheckBox('Config Pkt?')
        self.configCheckbox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.configCheckbox.setCheckState(Qt.CheckState.Unchecked)

        self.txDataField = QLineEdit()
        self.txDataField.returnPressed.connect(self.onSubmitTX)
        self.txTypeCombo = QComboBox()
        self.txTypeCombo.addItems(['Hex', 'Bin'])
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
        layout.addRow('RX Data:', self.rxDataLabel)
        layout.addRow('', txConfigRowLayout)
        layout.addRow('TX Data:', txRowLayout)
        layout.addRow('Errors:', self.errorLabel)
        layout.setVerticalSpacing(10)
        self.setLayout(layout)

    # On request to send to FIFO
    def onSubmitTX(self):
        res = write_to_FIFO(self.dev, self.mutex, self.pIndex, False, self.txDataField.text(), self.txTypeCombo.currentText()=='Hex')
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

    def displayRXData(self, data):
        self.rxDataLabel.append('Read: '+data+'\n')

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
        self.peripheralTabs = []
        for i in range(numPeripherals):
            self.peripheralTabs += [PeripheralTab(threadQueue, dev, i)]
            self.addTab(self.peripheralTabs[i], f'Peripheral {i}')
            print(f'Added Periph Tab #{i}')

        # Show the GUI
        self.show()

    def closeEvent(self, event):
        self.dev.close()


# Main #
if __name__ == '__main__':

    # Get the connected FTDI device
    dev = 0

    mutex = threading.Lock()

    app = QApplication(sys.argv)
    gui = LycanWindow(mutex, dev, 8)

    read_t = threading.Thread(target=read_from_FIFO, args=(dev, gui, mutex), daemon=True)

    # Start the reading thread
    read_t.start()

    sys.exit(app.exec())