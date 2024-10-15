// Wrapper for reconfigurable peripherals.
// All reconfigurable peripherals must share this interface.
// Make a copy of this file to create a new peripheral.

module reconfig_periph_wrapper
    (
        input logic clk,
        input logic rst,

        input logic[inputs_per_peripheral-1:0] in,
        output logic[outputs_per_peripheral-1:0] out,
        // For now, only need to tristate a subset of all outputs
        output logic[tristates_per_peripheral-1:0] tristate,

        // peripheral address is not stored in the local FIFOs.
        input logic[usb_packet_width-periph_address_width-1:0] tx_data,
        input logic tx_empty,
        output logic tx_read,
        
        output logic[usb_packet_width-periph_address_width-1:0] rx_data,
        output logic rx_valid,
        input logic rx_fifo_full,

        output logic idle
    );

    // Dummy module never transmits or receives...
    // Or do a loopback instead for testing?
endmodule