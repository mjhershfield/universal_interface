import sys
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QFormLayout, 
    QPushButton, QHBoxLayout, QCheckBox, QComboBox, QTextEdit,
    QTabWidget
)
from PyQt6.QtGui import QIntValidator, QColor
import lycan
import PyD3XX
from random import randint
import threading, time

# Constants #

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

# Globals #

lycanDev = None
mutex = None
gui = None

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
    
def write_to_FIFO(periphAddr, isConfig, data, format='Hex'):
    if(format!='Str'):
        data_num = str_to_num(data, format)
        # print(data_num)
        if(data_num != -1):
            # Convert integer packet to bytes object
            data_b = data_num.to_bytes(3, 'little')
            # Write to the FIFO
            mutex.acquire() # Acquire the I/O threading lock (blocking)
            num_bytes_written = lycanDev.write_data(periphAddr, data_b)
            mutex.release() # Release the threading lock
            return data_b, num_bytes_written
        else:
            return None, -1
    else:
        # Convert string to bytes object
        data_b = data.encode()
        # Write to FIFO
        mutex.acquire()
        print('Acquired lock to write')
        num_bytes_written = lycanDev.write_data(periphAddr, data_b)
        mutex.release()
        print('Released lock to write')
        return data_b, num_bytes_written
    
def CallBackFunction(CallbackType: int, PipeID_GPIO0: int | bool, Length_GPIO1: int | bool):
    print('Callback called')
    if(CallbackType == PyD3XX.E_FT_NOTIFICATION_CALLBACK_TYPE_DATA):
        print("CBF: You have " + str(Length_GPIO1) + " bytes to read at pipe " + hex(PipeID_GPIO0) + "!")
        mutex.acquire()
        print('Acquired lock to read')
        # For each packet received
        for i in range(int(Length_GPIO1/4)):
            isConfig, pId, data = lycanDev.read_packet()
            if(len(data) > 0):
                gui.peripheralTabs[pId].displayRXData(data.decode(), True)
        mutex.release()
        print('Released lock to read')
    return None

# Thread for reading from FIFO (Pauses if writing)
# def read_from_FIFO(lycanDev, GUI, mutex):
#     while(True):
#         mutex.acquire() # Acquire the I/O threading lock (blocking)
#         read_res = lycanDev.read_packet()
#         mutex.release() # Release the threading lock
#         if(read_res[2] != None and len(read_res[2]) > 0):
#             # Send the read packet to the corresponding peripheral tab
#             periphIndex = read_res[1]
#             data_in = read_res[2]
#             if(GUI.peripheralTabs[periphIndex]):
#                 GUI.peripheralTabs[periphIndex].displayRXData(data_in.decode()[::-1], True)
#         # Tell the main thread we are sleeping
#         time.sleep(0.100) # Sleep for 100 ms (CHANGE LATER???)
    
# Peripheral Tab Class #
class PeripheralTab(QWidget):

    # Constructor
    def __init__(self, peripheralIndex=0):
        super().__init__()

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
        self.txTypeCombo.addItems(['Str', 'Hex', 'Bin', 'Dec'])
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
        res = write_to_FIFO(self.pIndex, False, self.txDataField.text(), self.txTypeCombo.currentText())
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
            self.logData(res[0], False)

    def displayRXData(self, data, isRx):
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
    def __init__(self, numPeripherals):
        super().__init__()

        self.setWindowTitle("Lycan Universal Interface")
        self.setGeometry(200, 200, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Tab Setup #
        self.peripheralTabs = [0]*numPeripherals
        for i in range(0, numPeripherals):
            self.peripheralTabs[i] = PeripheralTab(i)
            self.peripheralTabs[i].initComponents()
            self.addTab(self.peripheralTabs[i], f'Peripheral {i}')
            print(f'Added Periph Tab #{i}')

        # Show the GUI
        self.show()

    def closeEvent(self, event):
        mutex.acquire()
        lycanDev.close()
        mutex.release()

# Main #
if __name__ == '__main__':

    # Instantiate Lycan device
    lycanDev = lycan.Lycan()
    status = PyD3XX.FT_SetNotificationCallback(lycanDev.ftdiDev, CallBackFunction)
    if status != PyD3XX.FT_OK:
        raise Exception('FAILED TO SET CALLBACK FUNCTION OF DEVICE 0: ABORTING')

    # Create mutex
    mutex = threading.Lock()

    app = QApplication(sys.argv)
    gui = LycanWindow(8)

    sys.exit(app.exec())