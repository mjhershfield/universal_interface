import sys
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QFormLayout, 
    QPushButton, QHBoxLayout, QCheckBox, QComboBox, QTextEdit,
    QTabWidget, QDialog, QDialogButtonBox, QVBoxLayout
)
from PyQt6.QtGui import QIntValidator, QColor, QCursor
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

# String to bytes method
def parse_input(inStr, format):
    res = 0
    if(format=='Dec'): # String is in decimal
        try:
            res = int(inStr)
        except:
            raise Exception('Parse error: Improper binary string')
    elif(format=='Bin'): # String is in binary
        for index, c in enumerate(inStr):
            if(c != '0' and c != '1'):
                raise Exception('Parse error: Improper binary string')
            res += (2**(23 - index)) * (ord(c) - 48)
    elif(format=='Hex'): # String is in hexadecimal
        for index, c in enumerate(inStr):
            if(c.isdigit() or ('a' <= c.lower() <= 'f')):
                if(c.isdigit()):
                    res += (16**(5 - index)) * (ord(c) - 48)
                else:
                    res += (16**(5 - index)) * (ord(c.lower()) - 87)
            else:
                raise Exception('Parse error: Improper hex string')
    # Now convert integer to bytes (unless the format is string)
    if(format=='Str'):
        res = inStr.encode()
    else:
        numBytes = (res.bit_length() + 7) // 8 # Can only support unsigned numbers right now
        res = res.to_bytes(numBytes, 'little')
    return res # Return the result
    
def write_to_FIFO(periphAddr, data, format='Hex'):
    try:
        # Parse user input
        data_b = parse_input(data, format)
    except:
        raise
    try:
        # Write to FIFO
        print('Write mutex acquired')
        mutex.acquire()
        num_bytes_written = lycanDev.write_data(periphAddr, data_b)
    except:
        mutex.release()
        raise
    print('Releasing')
    mutex.release()
    print('Write mutex released')
    return data_b, num_bytes_written

def config_to_FIFO(periphAddr, isWrite, regAddr, regVal):
    try:
        # Parse user input (as Hex)
        data_b = parse_input(regAddr, 'Hex')
        # Write to FIFO
        print('Write (config) mutex acquired')
        mutex.acquire()
        num_bytes_written = lycanDev.write_config_command(periphAddr, isWrite, regAddr, regVal)
    except:
        if(mutex.locked):
            mutex.release() # Make sure mutex is released, even on write error
        raise
    mutex.release()
    print('Write (config) mutex released')
    return data_b, num_bytes_written
    
def CallBackFunction(CallbackType: int, PipeID_GPIO0: int | bool, Length_GPIO1: int | bool):
    print('Callback called')
    if(CallbackType == PyD3XX.E_FT_NOTIFICATION_CALLBACK_TYPE_DATA):
        print("CBF: You have " + str(Length_GPIO1) + " bytes to read at pipe " + hex(PipeID_GPIO0) + "!")
        mutex.acquire()
        print('Acquired lock to read')
        # For each packet received
        for i in range(int(Length_GPIO1/4)):
            try:
                isConfig, pId, data = lycanDev.read_packet()
                if(len(data) > 0):
                    if(isConfig):
                        gui.peripheralTabs[pId].storeRegVal(data.encode())
                    else:
                        gui.peripheralTabs[pId].displayRXData(data, True)
            except Exception as e:
                gui.peripheralTabs[pId].errorLabel.setText(f'Error with reading in callback: {e}')
        mutex.release()
        print('Released lock to read')
    return None


# Peripheral Config Register Dialog Class #
class ConfigForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Information")
        self.addr_field = QLineEdit()
        self.value_field = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow('Register Address:', self.addr_field)
        form_layout.addRow('Register Value:', self.value_field)

        saveButton = QPushButton('Save')
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(saveButton, QDialogButtonBox.ButtonRole.AcceptRole)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(buttonBox)

        self.setLayout(main_layout)
    
    def get_inputs(self):
        return (self.addr_field.text(), self.value_field.text())

    
# Peripheral Tab Class #
class PeripheralTab(QWidget):

    # Constructor
    def __init__(self, parent, peripheralIndex=0):
        super().__init__(parent)

        self.pIndex = peripheralIndex
        self.logFile = None
        self.logging = False

    # Component Setup
    def initComponents(self): 
        self.logButton = QPushButton('Start Logging to File')
        self.logButton.setStyleSheet('background-color: green;')
        self.logButton.setFixedWidth(120)
        self.logButton.clicked.connect(self.createLogFile)

        self.configButton = QPushButton('Peripheral Config')
        self.configButton.setFixedWidth(120)
        self.configButton.clicked.connect(self.openConfigDialog)
        
        self.rxDataLabel = QTextEdit()
        self.rxDataLabel.setReadOnly(True)

        self.configCheckbox = QCheckBox('Config Pkt?')
        self.configCheckbox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.configCheckbox.setCheckState(Qt.CheckState.Unchecked)

        self.statusLabel = QLabel('Receiving...')
        self.statusLabel.setStyleSheet('color: green; font-weight: bold;')
        self.statusLabel.setFixedWidth(120)

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

        headerRowLayout = QHBoxLayout()
        headerRowLayout.addWidget(self.logButton, alignment=Qt.AlignmentFlag.AlignLeft)
        headerRowLayout.addWidget(self.configButton, alignment=Qt.AlignmentFlag.AlignRight)

        txConfigRowLayout = QHBoxLayout()
        txConfigRowLayout.addWidget(self.configCheckbox, alignment=Qt.AlignmentFlag.AlignRight)
        txConfigRowLayout.setSpacing(10)

        txRowLayout = QHBoxLayout()
        txRowLayout.addWidget(self.txDataField)
        txRowLayout.addWidget(self.statusLabel)
        txRowLayout.addWidget(self.txTypeCombo)
        txRowLayout.addWidget(self.txSubmitButton)

        layout = QFormLayout()
        layout.addRow(headerRowLayout)
        layout.addRow('RX Data:', self.rxDataLabel)
        layout.addRow('', txConfigRowLayout)
        layout.addRow('TX Data:', txRowLayout)
        layout.addRow('Errors:', self.errorLabel)
        layout.setVerticalSpacing(10)
        self.setLayout(layout)

    # On request to send to FIFO
    def onSubmitTX(self):
        self.setCursor(Qt.CursorShape.WaitCursor)
        self.statusLabel.setText('Transmitting...')
        self.statusLabel.setStyleSheet('color: red; font-weight: bold;')
        try:
            res = write_to_FIFO(self.pIndex, self.txDataField.text(), self.txTypeCombo.currentText())
        except Exception as e:
            print(f'Error {e}')
            self.errorLabel.setText(str(e))
        else:
            print('Successfully wrote')
            self.errorLabel.setText('') # Reset the error text box
            self.logData(res[0], False)
        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.statusLabel.setText('Receiving...')
            self.statusLabel.setStyleSheet('color: green; font-weight: bold;') # Reset status indicator back to receiving

    def displayRXData(self, data, isRx):
        print('Displaying text')
        if(self.txTypeCombo.currentText() == 'Hex'):
            self.rxDataLabel.insertPlainText("\n" + str(data.hex()))
        elif(self.txTypeCombo.currentText() == 'Dec'):
            self.rxDataLabel.insertPlainText("\n" + str(int.from_bytes(data, 'little')))
        elif(self.txTypeCombo.currentText() == 'Bin'):
            self.rxDataLabel.insertPlainText("\n" + str(bin(int.from_bytes(data, 'little'))))
        else:
            self.rxDataLabel.insertPlainText(data.decode())
        self.logData(data, True)

    def storeRegVal(self, data):
        print(data) # TODO

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

    def openConfigDialog(self):
        form = ConfigForm(self)
        result = form.exec() # Shows the dialog and waits for user interaction
        if result == QDialog.accepted:
            addr, val = form.get_inputs()
            

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
            self.peripheralTabs[i] = PeripheralTab(self, i)
            self.peripheralTabs[i].initComponents()
            self.addTab(self.peripheralTabs[i], f'Peripheral {i}')
            print(f'Added Periph Tab #{i}')

        # Show the GUI
        self.show()

    def closeEvent(self, event):
        mutex.acquire()
        try:
            PyD3XX.FT_ClearNotificationCallback(lycanDev.ftdiDev)
            lycanDev.close()
        except Exception as e:
            print(e)
        finally:
            mutex.release()
            event.accept()

# Main #
if __name__ == '__main__':

    # Instantiate Lycan device
    lycanDev = lycan.Lycan()

    # Check that the device is set up properly
    status, config = PyD3XX.FT_GetChipConfiguration(lycanDev.ftdiDev)
    if status != PyD3XX.FT_OK:
        raise Exception('FAILED TO READ CHIP CONFIG OF DEVICE 0: ABORTING')
    CH1_NotificationsEnabled = (config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1) != 0
    if not CH1_NotificationsEnabled:
        print('Config did not include noticification support, reconfiguring and cycling port')
        config.OptionalFeatureSupport = config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1
        PyD3XX.FT_SetChipConfiguration(lycanDev.ftdiDev, config)
        PyD3XX.FT_CycleDevicePort(lycanDev.ftdiDev)
        time.sleep(3)
        lycanDev.recreate_device()
        status, config = PyD3XX.FT_GetChipConfiguration(lycanDev.ftdiDev)
        if status != PyD3XX.FT_OK:
            raise Exception('FAILED TO READ CHIP CONFIG OF DEVICE 0: ABORTING')
        CH1_NotificationsEnabled = (config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1) != 0
        if not CH1_NotificationsEnabled:
            raise Exception('CH1 NOTIFICATIONS COULD NOT BE ENABLED: ABORTING')
        
    status = PyD3XX.FT_SetNotificationCallback(lycanDev.ftdiDev, CallBackFunction)
    if status != PyD3XX.FT_OK:
        raise Exception('FAILED TO SET CALLBACK FUNCTION OF DEVICE 0: ABORTING')

    # Create mutex
    mutex = threading.Lock()

    app = QApplication(sys.argv)
    gui = LycanWindow(8)

    sys.exit(app.exec())