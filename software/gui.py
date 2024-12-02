import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QFormLayout, 
    QPushButton, QHBoxLayout, QCheckBox, QComboBox, QTextEdit,
    QTabWidget
)
from PyQt6.QtGui import QIntValidator, QColor
import ftd3xx, threading, time
from ftd3xx.defines import *
import ftd3xx_functions as ftdi

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
    
def write_to_FIFO(dev, turn_lock, periphAddr, isConfig, data, isHex):
    global turn
    with turn_lock:
        turn = 'W' # Pause the reading thread
    packet_num = str_to_num(data, isHex)
    print(packet_num)
    if(packet_num != -1):
        # Convert integer packet to bytes object
        packet = packet_num.to_bytes(3, 'little')
        # Write to the FIFO
        num_bytes_written = ftdi.send_data_packet(dev, peripheral_addr=periphAddr, data=packet)
    else:
        return None, -1
    with turn_lock:
        turn = 'R' # Resume the reading thread
    return packet_num.to_bytes(3, 'little'), num_bytes_written

# Thread for reading from FIFO (Pauses if writing)
def read_thread(dev, GUI):
    global turn
    while(True):
        # Pause if it's writing's turn
        if(turn == 'R'):
            # Read from the FIFO
            data_in = ftdi.read_packet(dev)[1]
            print('Read:', data_in)
            if(data_in != None):
                # Send the read packet to the corresponding peripheral tab
                periphIndex = int.from_bytes(data_in, 'little') >> 29
                if(GUI.peripheralTabs[periphIndex]):
                    data = data_in[0:3]
                    GUI.peripheralTabs[periphIndex].displayRXData(str(hex(int.from_bytes(data, 'little'))))
        time.sleep(1000) # Sleep for 1 ms (may change this later)

# Peripheral Tab Class #
class PeripheralTab(QWidget):

    # Constructor
    def __init__(self, turn_lock, dev, peripheralIndex=0):
        super().__init__()

        self.turn_lock = turn_lock
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
        res = write_to_FIFO(self.dev, self.turn_lock, self.pIndex, False, self.txDataField.text(), self.txTypeCombo.currentText()=='Hex')
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
    def __init__(self, turn_lock, dev, numPeripherals):
        super().__init__()

        self.turn_lock = turn_lock
        self.dev = dev

        self.setWindowTitle("Lycan Universal Interface")
        self.setGeometry(200, 200, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Tab Setup #
        self.peripheralTabs = []
        for i in range(numPeripherals):
            self.peripheralTabs += [PeripheralTab(turn_lock, dev, i)]
            self.addTab(self.peripheralTabs[i], f'Peripheral {i}')
            print(f'Added Periph Tab #{i}')

        # Show the GUI
        self.show()


# Main #
if __name__ == '__main__':

    # Create a lock (used to set whose turn it is to use the FTDI - Read or Write)
    turn_lock = threading.Lock()

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

    app = QApplication(sys.argv)
    gui = LycanWindow(turn_lock, dev, 8)

    read_t = threading.Thread(target=read_thread, args=(dev, gui,), daemon=True)

    # Start the reading thread
    read_t.start()

    sys.exit(app.exec())