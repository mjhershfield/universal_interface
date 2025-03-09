// Wrapper for reconfigurable peripherals.
// All reconfigurable peripherals must share this interface.
// Make a copy of this file to create a new peripheral.

import lycan_globals::*;

module GPIO (
    input logic clk,
    input logic rst,

    input logic [16-1:0] in,
    (* mark_debug = "true" *) output logic [outputs_per_peripheral-1:0] out,
    // For now, only need to tristate a subset of all outputs
    (* mark_debug = "true" *) output logic [tristates_per_peripheral-1:0] tristate,

    // peripheral address is not stored in the local FIFOs.
    input logic [usb_packet_width-periph_address_width-1:0] tx_data,
    input logic tx_empty,
    output logic tx_rden,

    (* mark_debug = "true" *) output logic [usb_packet_width-periph_address_width-1:0] rx_data,
    (* mark_debug = "true" *) output logic rx_wren,
    input logic rx_full,

    output logic idle
);

  la_top #( .width(32) )logic_analyzer
  (
    .clk(clk), 
    .rst(rst),
    .packet_in(tx_data),
    .packet_out(rx_data),
    .pin_vals(in),
    .data_valid(rx_wren)
);  

assign tx_rden = 1'b0;



endmodule
