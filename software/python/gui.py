import sys
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt, pyqtSignal, pyqtBoundSignal, QObject, QTimer
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QFormLayout, 
    QPushButton, QHBoxLayout, QCheckBox, QComboBox, QTextEdit,
    QTabWidget, QDialog, QDialogButtonBox, QVBoxLayout, 
    QSplashScreen
)
from PyQt6.QtGui import QIntValidator, QColor, QTextCursor, QPixmap
import lycan
import PyD3XX
from random import randint
import threading, time
from threading import Lock
import pyqtgraph as pg
import os
import queue

# Constants #

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

# Globals #

lycanDev = None
mutex = None
gui = None

# Helper Functions #

def resource_path(relative_path):
    # Get the absolute path to resource, works for PyInstaller 
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Method to check the chip's config for notifications and to set the callback function
# Note: This should be run in a thread with a timeout, to avoid hanging function calls
def checkChipConfig():
    global lycanDev
    # Check that the device is set up properly
    status, config = PyD3XX.FT_GetChipConfiguration(lycanDev.ftdiDev)
    if status != PyD3XX.FT_OK:
        print('FAILED TO READ CHIP CONFIG OF DEVICE 0: ABORTING')
        os._exit(1)
    CH1_NotificationsEnabled = (config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1) != 0
    if not CH1_NotificationsEnabled:
        print('Config did not include notification support, reconfiguring and cycling port')
        config.OptionalFeatureSupport = config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1
        PyD3XX.FT_SetChipConfiguration(lycanDev.ftdiDev, config)
        if status != PyD3XX.FT_OK:
            print('FAILED TO WRITE CHIP CONFIG OF DEVICE 0: ABORTING')
            os._exit(1)
        lycanDev = lycan.Lycan()
        status, config = PyD3XX.FT_GetChipConfiguration(lycanDev.ftdiDev)
        if status != PyD3XX.FT_OK:
            print('FAILED TO READ CHIP CONFIG OF DEVICE 0: ABORTING')
            os._exit(1)
        CH1_NotificationsEnabled = (config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1) != 0
        if not CH1_NotificationsEnabled:
            print('CH1 NOTIFICATIONS COULD NOT BE ENABLED: ABORTING')
            os._exit(1)
        
    status = PyD3XX.FT_SetNotificationCallback(lycanDev.ftdiDev, gui.CallBackFunction)
    if status != PyD3XX.FT_OK:
        print('FAILED TO SET CALLBACK FUNCTION OF DEVICE 0: ABORTING')
        os._exit(1)
    else:
        print('Callback set successfully!')

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
   
# Peripheral Config Register Dialog Class #
class ConfigForm(QDialog):
    def __init__(self, parent, registerNames, registerVals):
        super().__init__(parent)
        self.setWindowTitle("Enter Information")
        self.registerNames=registerNames
        self.registerVals=registerVals

        self.addr_field = QComboBox()
        self.addr_field.addItems(self.registerNames)
        self.addr_field.currentIndexChanged.connect(self.handleAddrChange)
        self.value_field = QLineEdit(str(self.registerVals[0]))

        form_layout = QFormLayout()
        form_layout.addRow('Register Address:', self.addr_field)
        form_layout.addRow('Register Value:', self.value_field)

        saveButton = QPushButton('Save')
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(saveButton, QDialogButtonBox.ButtonRole.AcceptRole)
        buttonBox.accepted.connect(self.accept)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(buttonBox)

        self.setLayout(main_layout)

    def handleAddrChange(self, index):
        # Change the value in the 'Register Value' box
        self.value_field.setText(str(self.registerVals[index]))
    
    # Returns the inputs as integers (address field and value field)
    def get_inputs(self):
        return (int(self.addr_field.currentIndex()), int(self.value_field.text()))

# Peripheral Tab Parent Class - Inherited by each specific Peripheral type #
class PeripheralTab(QWidget):

    # Constructor
    def __init__(self, parent, peripheralIndex=0):
        super().__init__(parent)

        self.gui = parent
        self.pIndex = peripheralIndex
        self.logFile = None
        self.logging = False
        self.registerNames = ['Peripheral Type','1','2','3','4','5','6','7']
        self.registerVals = [-1, -1, -1, -1, -1, -1, -1, -1]
        self.initBaseComponents() # Initialize the basic components common to all peripheral tabs

    # Component Setup
    def initBaseComponents(self): 
        self.logButton = QPushButton('Start Logging to File')
        self.logButton.setStyleSheet('background-color: green;')
        self.logButton.setFixedWidth(120)
        self.logButton.clicked.connect(self.createLogFile)

        self.reloadFtdiButton = QPushButton('Reload Connection')
        self.reloadFtdiButton.setFixedWidth(120)
        self.reloadFtdiButton.clicked.connect(self.reconnectFtdi)

        self.configButton = QPushButton('Peripheral Config')
        self.configButton.setFixedWidth(120)
        self.configButton.clicked.connect(self.openConfigDialog)
        
        self.errorLabel = QTextEdit()
        self.errorLabel.setReadOnly(True)
        self.errorLabel.setFixedHeight(100)
        self.errorLabel.setTextColor(QColor(0xFF0000))

        # Layout Setup #

        self.headerRowLayout = QHBoxLayout()
        self.headerRowLayout.addWidget(self.logButton, alignment=Qt.AlignmentFlag.AlignLeft)
        self.headerRowLayout.addWidget(self.reloadFtdiButton, alignment=Qt.AlignmentFlag.AlignTrailing)
        self.headerRowLayout.addWidget(self.configButton, alignment=Qt.AlignmentFlag.AlignRight)

    # On request to reload the FTDI connection (via button click)
    def reconnectFtdi(self):
        global lycanDev

        # Close the existing device (in a seperate thread, with timeout of 1 second)
        thread = threading.Thread(target=lycanDev.close)
        thread.start()
        thread.join(timeout=1) # Set a timeout of 1 second (helps with lock ups after disconnections)

        # Re-instantiate the Lycan device
        try:
            lycanDev = lycan.Lycan()
        except Exception as e:
            print(e)

        # Check that it is set up correctly
        thread = threading.Thread(target=checkChipConfig)
        thread.start()
        thread.join(timeout=3)

        # Read the config registers again
        for p in range(8):
            for reg in range(8):
                gui.config_to_FIFO(p, False, reg, 0)

    def openConfigDialog(self):
        form = ConfigForm(self, self.registerNames, self.registerVals)
        result = form.exec() # Shows the dialog and waits for user interaction
        print(f'Form closed with result {result}')
        if result == 1:
            addr, val = form.get_inputs()
            if(self.registerVals[addr] != val): # If new value, send it to Lycan
                self.gui.config_to_FIFO(self.pIndex, True, addr, val) # Send a Write packet
                self.gui.config_to_FIFO(self.pIndex, False, addr, 0) # Send a Read packet to ensure register changed

    def storeRegValue(self, addr, val):
        self.registerVals[addr] = val

    # Must override in specific peripheral class
    def createLogFile(self):
        pass

    # Must override in specific peripheral class
    def logData(self, data, isRX):
        pass

    # Must override in specific peripheral class
    def displayData(self, data):
        pass

# Loopback Peripheral Tab Class #
class LoopbackTab(PeripheralTab):

    # Constructor
    def __init__(self, parent, peripheralIndex):
        super().__init__(parent, peripheralIndex)
        self.initComponents()

    # Component Setup
    def initComponents(self):

        self.rxDataLabel = QTextEdit()
        self.rxDataLabel.setReadOnly(True)

        self.txDataField = QLineEdit()
        self.txDataField.returnPressed.connect(self.onSubmitTX)
        self.txTypeCombo = QComboBox()
        self.txTypeCombo.addItems(['Str', 'Hex', 'Bin', 'Dec'])
        self.txSubmitButton = QPushButton('Send')
        self.txSubmitButton.clicked.connect(self.onSubmitTX)

        # Layout Setup #

        self.txRowLayout = QHBoxLayout()
        self.txRowLayout.addWidget(self.txDataField)
        self.txRowLayout.addWidget(self.txTypeCombo)
        self.txRowLayout.addWidget(self.txSubmitButton)

        layout = QFormLayout()
        layout.addRow(self.headerRowLayout)
        layout.addRow('RX Data:', self.rxDataLabel)
        layout.addRow('TX Data:', self.txRowLayout)
        layout.addRow('Errors:', self.errorLabel)
        layout.setVerticalSpacing(10)
        self.setLayout(layout)

    # On request to send to FIFO
    def onSubmitTX(self):
        # Create a writing thread and start it
        print('Writing')
        write_t = threading.Thread(target=self.gui.write_to_FIFO, args=(self.pIndex, self.txDataField.text(), self.txTypeCombo.currentText(),))
        write_t.start()

    # On received data
    def displayData(self, data):
        print('Displaying text')
        if(self.txTypeCombo.currentText() == 'Hex'):
            self.rxDataLabel.insertPlainText("\n" + str(data.hex()))
        elif(self.txTypeCombo.currentText() == 'Dec'):
            self.rxDataLabel.insertPlainText("\n" + str(int.from_bytes(data, 'little')))
        elif(self.txTypeCombo.currentText() == 'Bin'):
            self.rxDataLabel.insertPlainText("\n" + str(bin(int.from_bytes(data, 'little'))))
        else:
            try:
                self.rxDataLabel.insertPlainText(data.decode())
            except:
                self.rxDataLabel.insertPlainText(str(data))
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
                    try:
                        self.logFile.write(f'{timestamp}:\t{bytes(data)}\n')
                    except:
                        print('Error logging to file!')
            except Exception as e:
                print(e)
                self.errorLabel.setText('Error writing to log file!')

# UART Peripheral Tab Class #
class UARTTab(PeripheralTab):

    # Constructor
    def __init__(self, parent, peripheralIndex):
        super().__init__(parent, peripheralIndex)
        self.registerNames = ['Peripheral Type', 'Data Bits', 'Stop Bits', 'Parity', 'Baud Rate Div', '5', '6', '7']
        self.initComponents()

    # Component Setup
    def initComponents(self):

        self.rxDataLabel = QTextEdit()
        self.rxDataLabel.setReadOnly(True)

        self.txDataField = QLineEdit()
        self.txDataField.returnPressed.connect(self.onSubmitTX)
        self.txTypeCombo = QComboBox()
        self.txTypeCombo.addItems(['Str', 'Hex', 'Bin', 'Dec'])
        self.txSubmitButton = QPushButton('Send')
        self.txSubmitButton.clicked.connect(self.onSubmitTX)

        # Layout Setup #

        self.txRowLayout = QHBoxLayout()
        self.txRowLayout.addWidget(self.txDataField)
        self.txRowLayout.addWidget(self.txTypeCombo)
        self.txRowLayout.addWidget(self.txSubmitButton)

        layout = QFormLayout()
        layout.addRow(self.headerRowLayout)
        layout.addRow('RX Data:', self.rxDataLabel)
        layout.addRow('TX Data:', self.txRowLayout)
        layout.addRow('Errors:', self.errorLabel)
        layout.setVerticalSpacing(10)
        self.setLayout(layout)

    # On request to send to FIFO
    def onSubmitTX(self):
        # Create a writing thread and start it
        write_t = threading.Thread(target=self.gui.write_to_FIFO, args=(self.pIndex, self.txDataField.text(), self.txTypeCombo.currentText(),))
        write_t.start()

    # On received data
    def displayData(self, data):
        print('Displaying text')
        if(self.txTypeCombo.currentText() == 'Hex'):
            self.rxDataLabel.insertPlainText("\n" + str(data.hex()))
        elif(self.txTypeCombo.currentText() == 'Dec'):
            self.rxDataLabel.insertPlainText("\n" + str(int.from_bytes(data, 'little')))
        elif(self.txTypeCombo.currentText() == 'Bin'):
            self.rxDataLabel.insertPlainText("\n" + str(bin(int.from_bytes(data, 'little'))))
        else:
            try:
                self.rxDataLabel.insertPlainText(data.decode())
            except:
                self.rxDataLabel.insertPlainText(str(data))
        self.logData(data, True)
        self.rxDataLabel.moveCursor(QTextCursor.MoveOperation.End)

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
                    try:
                        self.logFile.write(f'{timestamp}:\t{bytes(data)}\n')
                    except:
                        print('Error logging to file!')
            except Exception as e:
                print(e)
                self.errorLabel.setText('Error writing to log file!')

# SPI-Master Tab Class #
class SPIMasterTab(PeripheralTab):

    # Constructor
    def __init__(self, parent, peripheralIndex):
        super().__init__(parent, peripheralIndex)
        self.initComponents()

    # Component Setup
    def initComponents(self):

        self.rxDataLabel = QTextEdit()
        self.rxDataLabel.setReadOnly(True)

        self.txDataField = QLineEdit()
        self.txDataField.returnPressed.connect(self.onSubmitTX)
        self.txTypeCombo = QComboBox()
        self.txTypeCombo.addItems(['Str', 'Hex', 'Bin', 'Dec'])
        self.txSubmitButton = QPushButton('Send')
        self.txSubmitButton.clicked.connect(self.onSubmitTX)

        # Layout Setup #

        self.txRowLayout = QHBoxLayout()
        self.txRowLayout.addWidget(self.txDataField)
        self.txRowLayout.addWidget(self.txTypeCombo)
        self.txRowLayout.addWidget(self.txSubmitButton)

        layout = QFormLayout()
        layout.addRow(self.headerRowLayout)
        layout.addRow('RX Data:', self.rxDataLabel)
        layout.addRow('TX Data:', self.txRowLayout)
        layout.addRow('Errors:', self.errorLabel)
        layout.setVerticalSpacing(10)
        self.setLayout(layout)

    # On request to send to FIFO
    def onSubmitTX(self):
        # Create a writing thread and start it
        write_t = threading.Thread(target=self.gui.write_to_FIFO, args=(self.pIndex, self.txDataField.text(), self.txTypeCombo.currentText(),))
        write_t.start()

    # On received data
    def displayData(self, data):
        print('Displaying text')
        if(self.txTypeCombo.currentText() == 'Hex'):
            self.rxDataLabel.insertPlainText("\n" + str(data.hex()))
        elif(self.txTypeCombo.currentText() == 'Dec'):
            self.rxDataLabel.insertPlainText("\n" + str(int.from_bytes(data, 'little')))
        elif(self.txTypeCombo.currentText() == 'Bin'):
            self.rxDataLabel.insertPlainText("\n" + str(bin(int.from_bytes(data, 'little'))))
        else:
            try:
                self.rxDataLabel.insertPlainText(data.decode())
            except:
                self.rxDataLabel.insertPlainText(str(data))
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
                    try:
                        self.logFile.write(f'{timestamp}:\t{bytes(data)}\n')
                    except:
                        print('Error logging to file!')
            except Exception as e:
                print(e)
                self.errorLabel.setText('Error writing to log file!')

# SPI-Student Tab Class #
class SPIStudentTab(PeripheralTab):

    # Constructor
    def __init__(self, parent, peripheralIndex):
        super().__init__(parent, peripheralIndex)
        self.initComponents()

    # Component Setup
    def initComponents(self):

        self.rxDataLabel = QTextEdit()
        self.rxDataLabel.setReadOnly(True)

        self.txDataField = QLineEdit()
        self.txDataField.returnPressed.connect(self.onSubmitTX)
        self.txTypeCombo = QComboBox()
        self.txTypeCombo.addItems(['Str', 'Hex', 'Bin', 'Dec'])
        self.txSubmitButton = QPushButton('Send')
        self.txSubmitButton.clicked.connect(self.onSubmitTX)

        # Layout Setup #

        self.txRowLayout = QHBoxLayout()
        self.txRowLayout.addWidget(self.txDataField)
        self.txRowLayout.addWidget(self.txTypeCombo)
        self.txRowLayout.addWidget(self.txSubmitButton)

        layout = QFormLayout()
        layout.addRow(self.headerRowLayout)
        layout.addRow('RX Data:', self.rxDataLabel)
        layout.addRow('TX Data:', self.txRowLayout)
        layout.addRow('Errors:', self.errorLabel)
        layout.setVerticalSpacing(10)
        self.setLayout(layout)

    # On request to send to FIFO
    def onSubmitTX(self):
        # Create a writing thread and start it
        write_t = threading.Thread(target=self.gui.write_to_FIFO, args=(self.pIndex, self.txDataField.text(), self.txTypeCombo.currentText(),))
        write_t.start()

    # On received data
    def displayData(self, data):
        print('Displaying text')
        if(self.txTypeCombo.currentText() == 'Hex'):
            self.rxDataLabel.insertPlainText("\n" + str(data.hex()))
        elif(self.txTypeCombo.currentText() == 'Dec'):
            self.rxDataLabel.insertPlainText("\n" + str(int.from_bytes(data, 'little')))
        elif(self.txTypeCombo.currentText() == 'Bin'):
            self.rxDataLabel.insertPlainText("\n" + str(bin(int.from_bytes(data, 'little'))))
        else:
            try:
                self.rxDataLabel.insertPlainText(data.decode())
            except:
                self.rxDataLabel.insertPlainText(str(data))
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
                    try:
                        self.logFile.write(f'{timestamp}:\t{bytes(data)}\n')
                    except:
                        print('Error logging to file!')
            except Exception as e:
                print(e)
                self.errorLabel.setText('Error writing to log file!')

# GPIO Peripheral Tab Class #
class GPIOTab(PeripheralTab):

    # Constructor
    def __init__(self, parent, peripheralIndex):
        super().__init__(parent, peripheralIndex)
        self.registerNames = ['Peripheral Type', 'Enable', 'Sample Rate Div', '3', '4', '5', '6', '7']
        self.initComponents()

    # Component Setup
    def initComponents(self):

        self.timeArr = list(range(50)) # 20 periods (depends on frequency of GPIO peripheral)
        self.dataArrs = [[0]*50]*16
        self.graphWidget = pg.PlotWidget()
        self.graphLegend = self.graphWidget.plotItem.addLegend(colCount=2)
        self.graphWidget.plotItem.getViewBox().disableAutoRange()
        self.graphWidget.plotItem.getViewBox().setXRange(-10, 50, padding=0.2)
        self.graphWidget.plotItem.setYRange(-1, 2, padding=0.1)
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'c', 'w', 'b', 'g', 'r', 'c', 'm', 'y', 'c', 'w']
        self.gpio_lines = [0]*16
        for i in range(16):
            self.gpio_lines[i] = self.graphWidget.plotItem.plot(self.timeArr, self.dataArrs[i], pen=colors[i], stepMode='left', name=f'Line {i}')
            if(i > 1):
                self.gpio_lines[i].setVisible(False)

        self.playing = False
        self.playButton = QPushButton('Start/Stop')
        self.playButton.clicked.connect(self.handlePlay)

        # Layout Setup #
        mainLayout = QFormLayout()
        mainLayout.addRow(self.headerRowLayout)
        mainLayout.addRow(self.playButton)
        mainLayout.addRow(self.graphWidget)
        mainLayout.addRow('Errors:', self.errorLabel)
        mainLayout.setVerticalSpacing(10)
        self.setLayout(mainLayout)

    def handlePlay(self):
        # Send a config packet to Lycan, enabling the GPIO to start receiving
        if(not self.playing):
            self.gui.config_to_FIFO(self.pIndex, True, 1, 1) # Set reg value to 1
            self.gui.config_to_FIFO(self.pIndex, False, 1, 0) # Read back the reg value
        else:
            self.gui.config_to_FIFO(self.pIndex, True, 1, 0) # Set reg value to 0
            self.gui.config_to_FIFO(self.pIndex, False, 1, 0) # Read back the reg value
        self.playing = not self.playing
        

    def displayData(self, data):
        dataInt = int.from_bytes(data, byteorder='little')
        for i in range(16):
            self.dataArrs[i] = self.dataArrs[i][1:]
            self.dataArrs[i].append((dataInt & (1 << i)) >> i)
            self.gpio_lines[i].setData(self.timeArr, self.dataArrs[i])
            if(i == 0):
                print(hex(dataInt))
        self.logData(data, True)
        pass

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
                    try:
                        self.logFile.write(f'{timestamp}:\t{bytes(data)}\n')
                    except:
                        print('Error logging to file!')
            except Exception as e:
                print(e)
                self.errorLabel.setText('Error writing to log file!')

# Main Window Class #
class LycanWindow(QTabWidget):

    # Dictonary holding the types of peripherals and the value of their 0 register
    PERIPHERAL_TYPES = {0: (LoopbackTab, 'Loopback'), 1: (UARTTab, 'UART'), 2: (GPIOTab, 'GPIO'), 3: (SPIMasterTab, 'SPI Master')}

    rx_update_signal = pyqtSignal(int, bytearray)
    config_update_signal = pyqtSignal(int, bytearray)
    error_update_signal = pyqtSignal(int, str)

    configReadQueues = [queue.Queue]*8
    configQueueLocks = [Lock]*8

    # Constructor
    def __init__(self, numPeripherals):
        super().__init__()

        self.rx_update_signal.connect(self.displayRXData)
        self.config_update_signal.connect(self.handleConfig)
        self.error_update_signal.connect(self.displayError)

        self.setWindowTitle("Lycan Universal Interface")
        self.setGeometry(200, 200, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Tab Setup #
        self.peripheralTabs = [PeripheralTab]*numPeripherals
        for i in range(0, numPeripherals):
            self.peripheralTabs[i] = GPIOTab(self, i)
            self.addTab(self.peripheralTabs[i], f'{i}: GPIO')
            print(f'Added Periph Tab #{i} of type {type(self.peripheralTabs[i]).__name__}')
            # Set up the config read queues, to keep track of what read config packets have been sent
            self.configReadQueues[i] = queue.Queue()
            self.configQueueLocks[i] = Lock()

    def write_to_FIFO(self, periphAddr, data, format='Hex'):
        try:
            # Parse user input
            data_b = parse_input(data, format)
        except Exception as e:
            print(f'Error {e}')
            self.error_update_signal.emit(periphAddr, f'Error with processing user input: {e}')
            return b'', 0
        # Write to FIFO
        numBytesWritten = 0
        mutex.acquire()
        print('Write mutex acquired')
        try:
            numBytesWritten = lycanDev.write_data(periphAddr, data_b)
        except Exception as e:
            print(f'Error {e}')
            self.error_update_signal.emit(periphAddr, f'Error writing to Lycan: {e}')
        else:
            print('Successfully wrote')
            self.error_update_signal.emit(periphAddr, f'') # Reset the error text box
            self.peripheralTabs[periphAddr].logData(data_b.decode(), False)
        finally:
            mutex.release()
            print('Write mutex released')
        return data_b, numBytesWritten

    def config_to_FIFO(self, periphAddr, isWrite, regAddr, regVal):
        try:
            # Write to FIFO
            mutex.acquire()
            print('Write (config) mutex acquired')
            num_bytes_written = lycanDev.write_config_command(periphAddr, isWrite, regAddr, regVal)
        except Exception as e:
            print(f'Error {e}')
            self.error_update_signal.emit(periphAddr, f'Error writing to Lycan: {e}')
        finally:
            mutex.release()
            print('Write (config) mutex released')

    def process_packet_thread(self, raw):
        try:
            print(f'Processing {len(raw)} bytes...')
            isConfig_arr, pId_arr, data_arr = lycanDev.interpret_raw_bytes(raw)
            # Now, do something based on each packet
            for i in range(len(isConfig_arr)):
                if(len(data_arr[i]) > 0):
                    if(isConfig_arr[i]):
                        self.config_update_signal.emit(pId_arr[i], data_arr[i])
                    else:
                        self.rx_update_signal.emit(pId_arr[i], data_arr[i])
                        self.error_update_signal.emit(pId_arr[i], '')
        except Exception as e:
            self.error_update_signal.emit(pId_arr[i], f'Error with processing read packet(s): {e}')
    
    # Reading callback function, called when there is data available in the FTDI chip's "in" FIFO
    def CallBackFunction(self, CallbackType: int, PipeID_GPIO0: int | bool, Length_GPIO1: int | bool):
        print('Callback called')
        if(CallbackType == PyD3XX.E_FT_NOTIFICATION_CALLBACK_TYPE_DATA):
            print("CBF: You have " + str(Length_GPIO1) + " bytes to read at pipe " + hex(PipeID_GPIO0) + "!")
            mutex.acquire()
            print('Acquired lock to read')
            # Read all bytes available
            try:
                numBytes, raw = lycanDev.read_raw_bytes(Length_GPIO1)
            except Exception as e:
                print(f'Error with reading in callback: {e}')
            finally:
                mutex.release()
                print('Released read lock')
            # Start a new thread to process the packet(s)
            process_t = threading.Thread(target=self.process_packet_thread, args=(raw,))
            process_t.start()
        return None

    # Method called when the rx_update signal is emitted
    def displayRXData(self, pIndex, data):
        self.peripheralTabs[pIndex].displayData(data)

    # Method called when the error signal is emitted
    def displayError(self, pIndex, errorStr):
        self.peripheralTabs[pIndex].errorLabel.setText(errorStr)

    # Method called when a configuration packet is received from Lycan (configUpdate signal is emitted)
    def handleConfig(self, pIndex, data_bytes):
        # Convert the data bytes to an integer
        addr = data_bytes[0]
        valB = data_bytes[1:4]
        val = int.from_bytes(valB, byteorder='little')
        # DEBUG print
        print('Received config packet: ', f'pId: {pIndex}', f'Address: {addr}', f'Value: {val}')
        if(addr == 0 and 0 <= val <= 2):
            # Check if the type of the peripheral has changed
            if(self.PERIPHERAL_TYPES[val][0] != type(self.peripheralTabs[pIndex])):
                print(f'Changing peripheral tab type from {type(self.peripheralTabs[pIndex])} to {self.PERIPHERAL_TYPES[val][0]}')
                self.removeTab(pIndex) # Remove the current tab
                self.peripheralTabs[pIndex] = self.PERIPHERAL_TYPES[val][0](self, pIndex) # Create the new tab
                self.insertTab(pIndex, self.peripheralTabs[pIndex], f'{pIndex}: {self.PERIPHERAL_TYPES[val][1]}') # Insert the new tab
            else:
                print('Config handled, but no valid change to peripheral type.')
        if(0 <= addr <= 7):
            self.peripheralTabs[pIndex].storeRegValue(addr, val)

    def closeEvent(self, event):
        # Start a thread that runs the close function for the Lycan device
        thread = threading.Thread(target=lycanDev.close)
        thread.start()
        thread.join(timeout=1) # Set a timeout of 1 second (helps with lock ups after disconnections)
        event.accept() # Accept the close event, closing the QT GUI Window

# Main #
if __name__ == '__main__':

    # Create mutex
    mutex = threading.Lock()

    app = QApplication(sys.argv)

    # Create and open a "Splashcreen" while loading
    splashImage = QPixmap(resource_path("splash_image.png"))  # Replace with your image file
    splash = QSplashScreen(splashImage, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()

    gui = LycanWindow(8)

    # Instantiate Lycan device
    lycanDev = lycan.Lycan()

    # Check that the device is set up properly
    status, config = PyD3XX.FT_GetChipConfiguration(lycanDev.ftdiDev)
    if status != PyD3XX.FT_OK:
        print('FAILED TO READ CHIP CONFIG OF DEVICE 0: ABORTING')
        os._exit(1)
    CH1_NotificationsEnabled = (config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1) != 0
    if not CH1_NotificationsEnabled:
        print('Config did not include notification support, reconfiguring and cycling port')
        config.OptionalFeatureSupport = config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1
        PyD3XX.FT_SetChipConfiguration(lycanDev.ftdiDev, config)
        if status != PyD3XX.FT_OK:
            print('FAILED TO WRITE CHIP CONFIG OF DEVICE 0: ABORTING')
            os._exit(1)
        lycanDev = lycan.Lycan()
        status, config = PyD3XX.FT_GetChipConfiguration(lycanDev.ftdiDev)
        if status != PyD3XX.FT_OK:
            print('FAILED TO READ CHIP CONFIG OF DEVICE 0: ABORTING')
            os._exit(1)
        CH1_NotificationsEnabled = (config.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1) != 0
        if not CH1_NotificationsEnabled:
            print('CH1 NOTIFICATIONS COULD NOT BE ENABLED: ABORTING')
            os._exit(1)
        
    status = PyD3XX.FT_SetNotificationCallback(lycanDev.ftdiDev, gui.CallBackFunction)
    if status != PyD3XX.FT_OK:
        print('FAILED TO SET CALLBACK FUNCTION OF DEVICE 0: ABORTING')
        os._exit(1)
    else:
        print('Callback set successfully!')

    # Read the peripheral config registers
    for p in range(8):
        for reg in range(8):
            gui.config_to_FIFO(p, False, reg, 0)

    splash.close() # Close the splashscreen
        
    gui.show() # Show the GUI

    os._exit(app.exec()) # Exit the program on GUI exit