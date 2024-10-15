// Static peripheral block - contains the reconfigurable logic and the FIFOs/etc.

module periph
    #(
        parameter logic[periph_address_width-1:0] ADDRESS
    )
    (
        input logic clk,
        input logic rst,

        input logic[inputs_per_peripheral-1:0] in,
        output logic[outputs_per_peripheral-1:0] out,
        // For now, only need to tristate a subset of all outputs
        output logic[tristates_per_peripheral-1:0] tristate,

        input logic[usb_packet_width-1:0] tx_data,
        input logic tx_valid,
        output logic tx_full,

        output logic[usb_packet_width-1:0] rx_data,
        input logic rx_read,
        output logic rx_empty,
        output logic rx_almost_full,
        output logic rx_full,

        output logic idle

    );


    // Instantiate reconfig_periph_wrapper
    // Connect to FIFOs (top bits of FIFOs are constant address)
    // This level strips out the address? or does the arbitrator handle it?
endmodule