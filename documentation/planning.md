# Planning Document

## OVERARCHING QUESTIONS (for first meeting)
- Team name
- Meeting time and frequency
- Which HDLs to use for design and verification?
- Who is in charge of what? (initially)
- Come up with goal for end of semester
- Come up with first deliverables from each team member (1-2 weeks of work)


### Ideas for first deliverables
- Peripherals: Implement and start testing UART
- Architecture: Create scaffolding for project HDL (common includes, I/O pins, initial interfaces for peripheral blocks, USB interface, top level)
- Interfacing: research bus arbitration techniques to decide whether to read/write from host, and which peripheral gets to send data back to the host at a given time.
- Software: Research how to use the D3XX driver set and research if it is possible to present our device as multiple virtual devices (like if we can present 3 UART peripherals as 3 serial interfaces so normal software can use them too). Is cross platform software (windows/linux) viable?
- Verification: Start learning SystemVerilog testbenching? Idk what we have to do for verification, maybe make models of how the system should work or ways to emulate DUT peripherals or the USB host sending/receiving data through the FIFO

if you were doing research, maybe add the best sites/papers to the references. pls give it at least a little time <3

## Timeline
- I need a gantt chart I swear


## Hardware

### Dev Board

Check the references section for the dev board's datasheet

### Future Considerations
- Level shifting I/O
- Over current protection
- Resistance measurements to ensure we don't drive outputs?


## Partial Reconfiguration Blocks

### Peripherals to Implement

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
    - x bit input (same as USB FIFO minus packet decoding logic)
    - FIFO empty input
    - Flush FIFO output
- RX data FIFO control signals
    - x bit output (same as USB FIFO minus packet decoding logic)
    - data valid output
    - FIFO full input
    - Flush FIFO output
- Configuration registers
    - Need to choose one
        - Put commands in the TX data FIFO, have the peripheral parse them and manage them
        - have an external input (RAM-style)
- General control signals
    - Idle output (safe to reconfigure)
    - Reset input (active high)
    - clock input lol (probably 100 MHz)


### RX and TX FIFOs
- should they be 32 bits wide so they can be sent directly back to the USB host without any additional processing?
- should they additionally have an "almost full" signal for prioritizing peripherals that may overflow

### Constraints

Coming soon. based of the limitations of partial reconfig

Need to make sure that everything will be able to route on a smaller FPGA still.

Are the external I/O pins crossing clock domains? yes.

## Peripheral Requirements

### UART
- Must run at 100 MHz
    - TX has a configurable clock divider to accommodate different baud rates
    - RX auto detects baud rate based on width of start bit?
- Configurable number of start bits
- Parity generation and checking - none, odd, even, mark, space

### SPI
- Must run at 100 MHz
- its just a shift register how bad can it be?
- can master/slave be a single peripheral or should it be 2?
- Master must have a clock divider so we can generate other frequencies
- Slave must handle clock domain crossing for sure?

more to come ...

## USB Interface

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
- Wakeup(L) bidirectional? check datasheet
- There are two configurable GPIO on the FIFO IC. what can they do?

### Bus Sharing/Arbitration

This might be something we have to find papers on. In my head, a round-robin approach for each of the peripherals would be good and there are several approaches to do that. How can we prioritize reads/writes over each other? does it make sense to do that?

Idea: round robin but priority given to FIFOs that are almost full? Need to look for papers

Trying to find links for bus arbitration circuit approaches
- TDM/counter approach (bad)
- Barrel shifter round robin (probably fine)
- unhinged double priority encoder round robin (citation needed)

## USB Protocol

Each packet through the FIFO is 32 bits. The FIFO has four channels, so we can theoretically use them to differentiate between peripherals or functions like data vs configuration. I'm not sure what the overhead of switching channels is, however.

Assumes <= 8 total peripherals (including default GPIO)

This protocol would be transmitted directly to the peripheral, minus the peripheral address field.

This protocol was pulled out of my ass to allow interleaving packets from different peripherals easily. It may make more sense if we are using one peripheral repeatedly to instead have a header/content style

### Idea 1: optimized interleaving

#### General packet:
|Name|Bit field|Notes|
|-|-|-|
|Peripheral Address|31-29|Ranges from 0-7|
|Configuration Flag|28|0 = data for tx/rx|
|Number of valid bytes|27-26|1-3 bytes in data field of this packet|
|Data for peripheral|25-0|Peripheral dependent format?|

#### Configuration Packet:
|Name|Bit field|Notes|
|-|-|-|
|Peripheral Address|31-29|Ranges from 0-7|
|Configuration Flag|28|0 = data for tx/rx|
|Read/Write|27|0=read, 1=write|
|Configuration register address|26-24|Peripheral dependent?|
|New value of register|23-0|ignored for reads. bottom bits of this field are used|

Alternatively, multiple channels could be used instead of the configuration flag (eg. send config on channel 0, data on channel 1), freeing a bit from every packet. I don't know what time cost is associated with switching channels on the FPGA side.

### Idea 2: optimized streaming

START PACKET

Data using up the full amount

END PACKET

This requires the bus arbiter to know which peripheral should control the stream instead of just sending packets everywhere

What format should we use for start and end to distiguish them from the data packets while still making sure we aren't getting false positives from valid data? can we use channels for this?

### Any other ideas?

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


### FTDI FT601 USB to FIFO
- [FT601 USB FIFO IC Device Info](https://ftdichip.com/products/ft601q-b/)
- [FT601 Dev Board Device Info](https://ftdichip.com/products/umft601x-b/)
- [D3XX (FTDI USB3 Driver) Info](https://ftdichip.com/drivers/d3xx-drivers/)