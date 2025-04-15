# Lycan Senior Design Project

Matthew Hershfield, Adam Bracci, Gilon Kravatsky, Matthew Self, Andres Muskus (MAGMA 🔥)

Lycan aims to be a _universal interface_ for common digital protocols used in embedded devices such as UART and SPI. Lycan's flexible architecture allows up to 8 supported communication peripherals to share a single USB bus, whether that is 8 UARTs, a SPI and a JTAG, or logic analyzer functionality.


## Current Status
  
### Peripherals
- UART
- GPIO
- Loopback
- SPI Master (Integration Testing In-Progress)
- SPI Student (Integration Testing In-Progress)

### Other Features
- Modular Architecture
  - Any combination of up to 8 peripherals can be specified at compile time
  - Any set of pin assignments to those peripherals can be specified at compile time
- Configuration Registers
  - Configurable stop bits, parity, and baud rate for UART
  - Configurable sample rate and enable register for GPIO
- Lycan Logic-Level-Conversion Board
  - 3.3V to 5V logic levels, with on-board 5V reference
  - If peripheral logic level is not 3.3V or 5V, external reference can be provided
- Lycan GUI
  - Auto detects the peripherals currently used on Lycan and configures the tabs in the GUI to match.
  - The GUI supports reading/sending data from all peripheral types and reading/modifying their config registers


## Current Bugs
### Opening GUI while FIFO full

Sometimes opening the GUI after the device has been running, specifically with the GPIO peripheral, which can quickly fill the FIFO, can cause the GUI to hang and not fully open

Current Fix: Press the reset button and re-open the GUI. If the GUI does not open, disconnect and reconnect the USB to the host PC and try again.

Frequency: Generally not frequent, since 4/13 (Added GPIO enable register)

### FTDI Function Hang Bug

On startup, during a FTDI read or write function call, the chip may get stuck. The origin of this is unknown, and there is no way to debug the function call (locked behind a DLL).

Current Fix: Press the reset button and re-open the GUI. If the GUI does not open, disconnect and reconnect the USB to the host PC and try again.

Frequency: Not frequent, but can often occur if board is not initially reset after programming a new bitstream

### Random Windows & FTDI-related Connection Bugs

On startup of the GUI, sometimes the FTDI device is not detected. This is a problem with the way some computers connect/disconnect to USB devices.

Fix: Unplug and plug in the USB cable on the computer side, and try again

### Hardware Bugs

- Peripheral WHOAMI configuration registers are not read-only
- If a configuration packet is read on the same cycle as data arrives from the communication peripheral, the data from the communication peripheral will be lost
- FT601 technically does not have its timing constraints met. This may be improved by using multicycle paths and increasing the FPGA clock frequency, but we have not run into many issues beyond the critical warnings after implementation in Vivado.


## Hardware Info

### Architecture

Lycan is built on top of an Artix-7 FPGA to enable its reconfigurability, specifically the Nexys Video development board. We also use the FT601Q on the UMFT601X-B development board to allow Lycan to communicate over USB. The general architecture of Lycan is described below.

The host PC and Lycan communicate using the Lycan Peripheral Interface (LPI) protocol through the FT601Q IC. FIFOs are placed between the main Lycan RTL on the FPGA and the FT601Q to insulate the FT601Q from timing changes within the design. Each individual communication peripheral also has local RX and TX buffers to ensure that no data is lost if a large burst needs to travel into or out of that peripheral. Data in the TX FIFOs is read by each individual peripheral, and it is up to the peripheral implementer how to interpret the configuration data or TX data in each packet. When data is being sent from a peripheral back to the host PC, it is first written to the local RX FIFO of the peripheral. Then, a round robin bus arbiter manages the sharing of the FT601Q's FIFO interface to send data back to the host PC.


### Adding a new peripheral

A key goal of Lycan is to make it easy for users to create and integrate their own custom communication peripherals. We have made major strides in this area, and it should be possible for experienced RTL designers to integrate with Lycan.

The ports implemented by every peripheral are shown in [reconfig_periph_wrapper](./hdl/reconfig_periph_wrapper.sv) They include:
```sv
module reconfig_periph_wrapper (
    input logic clk,
    input logic rst,

    // I/O that connects to the DUT
    input logic [inputs_per_peripheral-1:0] in,
    output logic [outputs_per_peripheral-1:0] out,
    output logic [tristates_per_peripheral-1:0] tristate,

    // TX fifo read end (data being sent to DUT)
    // Peripheral address is not stored in the local FIFOs.
    input logic [usb_packet_width-periph_address_width-1:0] tx_data,
    input logic tx_empty,
    output logic tx_rden,

    // RX FIFO write end (data being sent back to host)
    output logic [usb_packet_width-periph_address_width-1:0] rx_data,
    output logic rx_wren,
    input logic rx_full,

    // Output 1'b1 if the peripheral is not currently transmitting or receiving.
    // Currently unused.
    output logic idle
);
```

We recommend basing your peripheral on our [UART implementation](./hdl/periph/uart/uart.sv), which has additional features including configurable clock division, configuration registers, and width conversion between the 24 bits of data stored in a packet and the 8 bits that are transmitted/received at a time by the UART. Once you have implemented your peripheral, add a variant to the [periph_type_t enum](./hdl/lycan_globals.sv) and then add an instantiation of your peripheral to [periph.sv](./hdl/periph.sv) so that it can be instantiated at compile time.

## Software Info
See Releases for .exe file (Windows Only)
See the /software README file for information about setting up a Python environment
