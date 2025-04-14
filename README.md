# Lycan Senior Design Project

Team Members:
Matthew Hershfield, Adam Bracci, Gilon Kravatsky, Matthew Self, Andres Muskus

## Current Status (Completed so far)
Key:
- Hardware (H) - Verilog code complete and tested in simulation
- Software (S) - Python code complete (in the GUI.py program)
- Integrated (I) - Hardware code integrated with other peripherals and modules
- Tested (T) - Software and hardware tested and working well

### Peripherals
- UART (HSIT)
- GPIO (HSIT)
- Loopback (HSIT)
- SPI Master (HS)
- SPI Student (HS)

### Other Features
- Configuration Registers (HSIT)
  - Configurable stop bits, parity, and baud rate for UART
  - Configurable sample rate and enable register for GPIO
- Lycan Logic-Level-Conversion Board (HIT)
  - 3.3V to 5V logic levels, with on-board 5V reference
  - If peripheral logic level is not 3.3V or 5V, external reference can be provided


## Current Bugs
Opening GUI while FIFO full
Sometimes opening the GUI after the device has been running, specifically with the GPIO peripheral, which can quickly fill the FIFO, can cause the GUI to hang and not fully open
Current Fix: Press the reset button and re-open the GUI. If the GUI does not open, disconnect and reconnect the USB to the host PC and try again.
Frequency: Generally not frequent, since 4/13 (Added GPIO enable register)

FTDI Function Hang Bug
On startup, during a FTDI read or write function call, the chip may get stuck. The origin of this is unknown, and there is no way to debug the function call (locked behind a DLL).
Current Fix: Press the reset button and re-open the GUI. If the GUI does not open, disconnect and reconnect the USB to the host PC and try again.
Frequency: Not frequent, but can often occur if board is not initially reset after programming a new bitstream

Random Windows & FTDI-related Connection Bugs
On startup of the GUI, sometimes the FTDI device is not detected. This is a problem with the way some computers connect/disconnect to USB devices.
Fix: Unplug and plug in the USB cable on the computer side, and try again


## Design Plan Information - Hardware

### Dev Boards
- Using the Nexys Video dev board for FPGA development
- Using the UFT601X-B FTDI FIFO dev board for the USB protocol development and FIFO link to FPGA


### Future Considerations
- Level shifting I/O
- Over current protection
- Resistance measurements to ensure we don't drive outputs?


### Partially Reconfigured Peripherals to Implement

For protocols with bidirectional wires, I allocated them 1 input and 1 output for each bidirectional signal. Peripherals will have to manage tri-stating their outputs as needed.

|Peripheral|# inputs|# outputs|Notes|
|----------|--------|---------|-----|
|UART|1|1|
|SPI master|1|3|
|SPI Slave|3|1|
|I2C Master|1|2|Open drain and pullup required|
|I2C Slave|2|1|Open drain and pullup required|
|JTAG|1|4|
|SWD|1|2|One line is bidirectional


### Shared Interface for each Peripheral
- 3 inputs from the DUT
    - each input is one signal, just high or low
- 4 outputs to the DUT
    - each output consists of two signals: a high/low output signal and a signal controlling whether the output is tristated. this will enable safe bidirectional and open-drain I/O
- TX data FIFO control signals
    - 29 bit input (same as USB FIFO minus peripheral address)
    - FIFO empty input
    - Read TX data output
- RX data FIFO control signals
    - 29 bit output (same as USB FIFO minus peripheral address)
    - data valid output
    - FIFO full input
- Configuration registers
    - Configuration commands just get passed into the peripheral through the TX FIFO (see protocol section)
    - Probably want at minimum a self-clearing reset as a configuration register.
- General control signals
    - Idle output (safe to reconfigure)
    - Reset input (active high)
    - clock input lol (probably 100 MHz)


### RX and TX FIFOs
- 32 bits wide so they can be sent directly back to the USB host without any additional processing
- Use an "almost full" signal for prioritizing peripherals that may overflow


### Constraints

Coming soon. based off the limitations of partial reconfig

Need to make sure that everything will still be able to route on a smaller FPGA.

Are the external I/O pins crossing clock domains? yes. Do we need multiple layers of registers on our GPIO inputs to account for possible metastability? Maybe we test it lol


### Peripheral Requirements

### UART
- Must run at 100 MHz
    - TX has a configurable clock divider to accommodate different baud rates
    - RX auto detects baud rate based on width of start bit?
- Configurable number of stop bits
- Parity generation and checking - none, odd, even, mark, space

### SPI
- Must run at 100 MHz
- can master/slave be a single peripheral or should it be 2?
- Master must have a clock divider so we can generate other frequencies
- Slave must handle clock domain crossing for sure?

more to come ...

### USB Interface

### Pins required (directions wrt the FPGA)
See pages 7-10 of the IC datasheet
- Clock input (FIFO IC drives FPGA clock)
- FIFO data[31..0] output
- FIFO byte enable[3..0] output
- TX FIFO space available input
- RX FIFO data available input
- Write enable(L) output
- Read enable(L) output
- Output enable (L) output
- Reset(L) output
- Wakeup(L) bidirectional?

### Bus Sharing/Arbitration

Implementation plan: Barrel shifter approach for priority-driven round robin.

Each peripheral has a request signal to signal that they have data they want to transmit (FIFO empty). The arbiter controls which peripheral's data is sent back to the host computer using a grant signal (0-7)

## USB Protocol

Each packet through the FIFO is 32 bits. We will be using a single channel in the FIFO (FT232 mode), since this appears to be the simplest & most performant method to use the IC.

We will have 8 total peripherals on Lycan at all times (including the default GPIO R/W)

This protocol would be transmitted directly to the peripheral, minus the peripheral address field. The peripheral address is handled by a wrapper around each peripheral to reduce boilerplate in the reconfigurable peripherals.

This protocol was designed to allow interleaving packets from different peripherals easily. 

### Data From Host To Lycan Packet:
|Name|Bit field|Notes|
|-|-|-|
|Peripheral Address|31-29|Ranges from 0-7|
|Configuration Flag|28|0 = data for tx/rx|
|Number of valid bytes|27-26|1-3 bytes in data field of this packet|
|Reserved|25-24|Currently unused|
|Data for peripheral|23-0|Up to 3 bytes of data|

### Data From Lycan To Host Packet:
|Name|Bit field|Notes|
|-|-|-|
|Peripheral Address|31-29|Ranges from 0-7|
|Configuration Flag|28|0 = data from peripheral|
|Number of valid bytes|27-26|1-3 bytes in data field of this packet|
|Reserved|25-24|Currently unused|
|Data for peripheral|23-0|Up to 3 bytes of data|

### Configuration Packet from Host to Lycan:
|Name|Bit field|Notes|
|-|-|-|
|Peripheral Address|31-29|Ranges from 0-7|
|Configuration Flag|28|0 = data for tx/rx|
|Read/Write|27|0=read, 1=write|
|Configuration register address|26-24|Peripheral dependent?|
|New value of register|23-0|ignored for reads. bottom bits of this field are used|

### Configuration From Lycan To Host Packet:
|Name|Bit field|Notes|
|-|-|-|
|Peripheral Address|31-29|Ranges from 0-7|
|Configuration Flag|28|1 = data from config register|
|Number of valid bytes|27-26|1-3 bytes in data field of this packet|
|Reserved|25-24|Currently unused|
|Data for peripheral|23-0|Up to 3 bytes of data|


## References & Documentation

### General Digital Design
- [Stitt's VHDL lessons](https://github.com/ARC-Lab-UF/vhdl-tutorial)
- [Stitt's SV lessons](https://github.com/ARC-Lab-UF/sv-tutorial)
- [Stitt's timing lessons](https://github.com/ARC-Lab-UF/intel-training-modules/tree/master/timing)
- [Past Reconfig 1 materials](http://www.gstitt.ece.ufl.edu/courses/fall23/eel4720_5721/index.html)
- [Past Reconfig 2 materials](http://www.gstitt.ece.ufl.edu/courses/spring23/eel6935_4930/index.html)

### FPGA/Partial Reconfiguration
- [Nexsys Video Artix-7 Dev Board Device Info](https://digilent.com/shop/nexys-video-artix-7-fpga-trainer-board-for-multimedia-applications/)
- [Vivado Documentation for DFX](https://docs.amd.com/r/en-US/ug909-vivado-partial-reconfiguration/Introduction)
- [Guided tutorial from 01signal](https://www.01signal.com/vendor-specific/xilinx/partial-reconfiguration/)

### Vivado Tools & Tips
- [Version Control and Vivado](https://adaptivesupport.amd.com/s/article/Revision-Control-with-a-Vivado-Project?language=en_US)

### FTDI FT601 USB to FIFO
- [FT601 USB FIFO IC Device Info](https://ftdichip.com/products/ft601q-b/)
- [FT601 Dev Board Device Info](https://ftdichip.com/products/umft601x-b/)
- [D3XX (FTDI USB3 Driver) Info](https://ftdichip.com/drivers/d3xx-drivers/)
