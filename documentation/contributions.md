# Contribution Log

## 09/26/24
- Matthew H: Create Github repository and initial design planning (2 hr)

## 10/1/24
- All: Meet up to decide on meeting times, initial deliverables. (1 hr)

## 10/6/24
- Matthew S: Start Design Plan Draft - 1 hour

## 10/7/24
- Adam B: Watched youtube tutorials on system verilog - 2 hour
- Adam B: Read some articles on bus arbitration strategies - 1 hour

## 10/8/24
- All: Meet up to work on Design Plan Draft and iron out details on USB protocol & bus arbitration (2 hr)

## 10/9/24
- Matthew H: proofread and edit Design Plan Draft, create statement of work (1 hr)
- Matthew S: finish statement of work milestones, final proofreading (30 minutes)
- Matthew H: Start learning SystemVerilog, begin scaffolding the HDL structure. (2 hr)
- Gilon K: Began learning SV (2 hr)

## 10/15/24
- All: Meet up to define requirements for pre-alpha build (1 hr)

## 10/21/24
- Matthew S: Research ftd3xx python source code (2 hours)
- Matthew S: Create initial python script for reading and writing data to USB FIFO (3 hrs)
- Gilon K: Dug into spec of FT601 Device (2 Hr)

## 10/22/24
- All: Meet to check on progress, define final goals for pre-alpha build, check on dev board arrivals. (30 minutes)
- Matthew H: Update planning document, add Vivado project to version control (1 hour)
- Matthew S: Test out python ftd3xx module with FTDI FIFO board, identification/connection (1 hour)

## 10/23/24
-Adam B: Read through a lot of Stitt's system verilog tutorial and practiced simulating - 2 hour

## 10/24/24
- All: Meet to work on Pre-Alpha build, further develop hardware architecture and write source code (2 hours)
- Matthew S: Work on the usage of pipes within the FIFO board, and how to properly read/write from them using Python (1 hour)
- Adam B: Worked on programming the arbiter - 3 hours
- Matthews, Adam: Continued work on writing Pre-Alpha Build Document (2 hours)
- Gilon K: Further dug into FT601 spec (1 hr)
- Gilon K: Designed FSM for FT601 (1.5 hr)
- Gilon K: Wrote FSM for FT601 controller in SV (2 Hr)

## 10/29/24
- All: Meet to discuss the week's goals (1 hr)

## 10/31/24
- Matthew S: Work on writing to the FIFO (without being connected to the FPGA) (2 hrs)

## 11/4/24
- Matthew S: Contact FTDI about FIFO communication issues, and research/try-out Python GUI options (2 hrs)

## 11/5/24
- All: Meet to discuss the week's goals, any blocking issues, and open the FPGA board (1 hr)

## 11/7/24
- All: Meet to work on verification and integration of hardware components (2 hrs)

## 11/12/24
- All: Check-in with Carsten, start work to get Lycan working on the dev board (2 hrs)

## 11/14/24
- All: Continue work debugging Lycan on the FPGA (2 hrs)

## 11/15/24
- Matthew S: Work on fixing FTDI FIFO Clk configuration issue, measuring with scope (2 hrs)
- Matthew S: Explore FTDI-provided Python source code for a loopback test - compare to own code (0.5 hrs)

## 11/19/24
- All: Continue to debug Lycan and FTDI, running tests (2 hrs)
- Matthew S: Fix Clock issue - for good (after talking with FTDI support) (1 hr)

## 11/20/24
- Matthew S: Work on GUI prototype, add multiple tabs for 8 peripherals (1 hr)

## 11/21/24
- Matthew S: Test lycan_loopback.py & gui.py programs with the FPGA connected (1 hr)
- Adam B, Matthew H, Gilon K: Discuss HW design and new GPIO peripheral (1 hr)

## 11/29/24
- Matthew S: Research Python packaging using pyinstaller, make the GUI and .exe for Windows (2 hrs)

## 12/16/24
- Matthew H: Prototype a Rust program for interacting with Lycan (4 hrs)

## 12/22/24
- Matthew H: Test different strategies for meeting timing constraints of FT601: adding registers, adjusting clock freq (3 hrs)

## 12/27/24
- Matthew S: Worked on cleaning up the Python code-base, standardized endianness of packets in SW (3 hrs)

## 1/3/25
- Matthew H: Added a layer of FIFOs between Lycan and the FT601, locked P&R to eliminate metastability (3 hrs)

## 1/4/25
- Matthew H: Solved issue where a peripheral sent 50+ copies of the first byte it received from the host. (1 hr)

## 1/6/25
- Matthew H: Identified problem of an undersized read buffer causing dropped packets, tested software mitigations (2 hrs)

## 1/14/25
- All: Meet to discuss upcoming semester, create Github Projects tasks (1 hr)

## 1/16/25
- All: Work on Lycan hardware (UART peripheral) and software (fix lock-up on GUI) (2 hrs)
- Matthew S: Create thread-safe mutex structure for GUI multithread reads (2 hrs)
- Adam and Matthew H: Refactor and testbench UART RX module to enable different configurations (2 hrs)
- Gilon: Started design of GPIO peripheral (2 hrs)

## 1/21/25
- All: Work on hardware (UART peripheral), integration, and software (lost packets) (2 hrs)
- Matthew H: Debug the FPGA datapath for packet dropping issue (1 hr)
- Matthew S: Contact FTDI and debug the software to see why every other packet is being lost (1 hr)
- Gilon: Created clk_div module (2 hr)

## 1/23/25
- All: Meet to work on hardware and software (1 hr)
- Adam: Work on UART tx module and design specifications for packet error handling (1 hr)
- Gilon: Created self checking tb for clk_div and debugged clk_div (2 hr)

## 1/25/25
- Matthew S: Work on simulated FTDI python script for testing GUI without FPGA (2 hrs)

## 1/28/25
- All: Instructor and Stakeholder meetings (30 min)
- All: Discuss future plans and get updated on current progress (30 min)
- Matthew S: Begin PCB schematic, research feasibility/costs (1 hr)
- Adam: Work on debugging Vivado simulation issue causing system deadlock to occur (3 hrs)
- Gilon: Created logic analyzer module and self checking tb (2 hr)

## 1/29/25
- Adam: Work on testbenching and debugging UART tx across different input waveforms (3 hrs)

## 1/30/25
- Matthew S: Work on software (GUI logger feature) (2 hrs)
- Matthew S: Work on Alpha Report and Test Plan (1 hr)
- Adam and Matthew H: Work on integrating UART module into rest of system and initial testbenching (2 hrs)


## 1/31/25
- All: Finish Alpha Build Report and Test Plan (_ hrs)

## 2/4/25
- Adam: Started working on SPI modules and assited with UART system level debug (3 hrs)
- Gilon: Started top level entity for logic analyzer module (2 hr)

## 2/6/25
- Adam: Finished designing SPI modules and designed a testbench to test both M and S functionality (3 hrs)
- Gilon: Continued working on top level entity for LA (2 hr)

## 2/11/25
- All: Meet to work on UART testing and discuss plans (2 hrs)

## 2/12/25
- Matthew S: Research logic-level conversion circuits & chips (1 hr)
- Matthew S: Simulate LLC circuits in LTSpice and draft initial PCB circuit (3 hrs)
- Gilon: finished working on top level entity for LA and created tb (2 hr)

## 2/13/25
- All: Meet with Carsten (15 min)
- Matthew S: Work on testing C++ software, notifications (3 hrs)

## 2/14
- Matthew S: Work on C++ GUI using QT Creator (3 hrs)
- Gilon: integrated LA into template for peripherals (1 hr)
- Gilon: debugged issue with git push (1 hr)

## 2/15
- Matthew S: Work on QT Creator project for making C++ GUI (3 hrs)

## 2/17
- Matthew S: Test C++ code in the lab, using UART (2 hrs)

## 2/18
- All: Meet to work on UART peripheral and software (2 hrs)

## 2/19
- Matthew S: Test Python and C++ code further in lab, check for packet drops (1 hr)

## 2/20
- All: Meet to finish up UART peripheral receiving and software (switch back to Python) (2 hrs)
- Matthew S: Test new Python module and create simple Lycan API using it (2 hrs)
- Matthew S: Finish LLC board PCB layout and order boards (2 hrs)

## 2/21
- All: Work on Beta test plan and documentation (_ hrs)

## 2/24
- All: Finish Beta Build Report and video (2 hrs)

## 2/25
- All: Stakeholder meeting (15 min)
- Gilon: work to integrate GPIO periph (3.5 hr)

## 2/27
- All: Stakeholder meeting (15 min)
- Gilon: continue work to integrate GPIO periph (2 hr)

## 3/3
- Gilon: continue work to integrate GPIO periph (1 hr)

## 3/4
- Gilon and Adam: Debug integration of GPIO periph (2.5 hr)

## 3/5
- Gilon and Adam: Debug integration of periphs (7.5 hr)

## 3/6
- All: Debug integration of periphs and prep for beta presentation (3 hr)
