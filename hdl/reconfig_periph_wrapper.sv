// Wrapper for reconfigurable peripherals.
// All reconfigurable peripherals must share this interface.
// Make a copy of this file to create a new peripheral.

import lycan_globals::*;

module reconfig_periph_wrapper (
    input logic clk,
    input logic rst,

    input logic [inputs_per_peripheral-1:0] in,
    output logic [outputs_per_peripheral-1:0] out,
    // For now, only need to tristate a subset of all outputs
    output logic [tristates_per_peripheral-1:0] tristate,

    // peripheral address is not stored in the local FIFOs.
    input logic [usb_packet_width-1:0] tx_data,
    input logic tx_empty,
    output logic tx_read,

    output logic [usb_packet_width-1:0] rx_data,
    output logic rx_valid,
    input logic rx_fifo_full,

    output logic idle
);

  // Dummy module never transmits or receives...
  // Or do a loopback instead for testing?

  // Assign tristates and outputs to constant values
  logic tx_read_valid_r, rx_valid_r;

  // Need to buffer tx read valid signal to account for 1 cycle read latency.
  // always_ff @(posedge clk or posedge rst) begin
  //   if (rst == 1) begin
  //     tx_read_valid_r <= 1'b0;
  //     rx_valid_r <= 1'b0;
  //   end else begin
  //     tx_read_valid_r <= tx_read;  // cycle of latency
  //     rx_valid_r <= tx_read_valid_r;
  //   end
  // end

  assign tx_read = ~tx_empty;
  assign rx_data = tx_data;
  // assign rx_valid = rx_valid_r;
  assign rx_valid = tx_read;
  // FIX LATER?
  assign idle = ~(tx_read | tx_read_valid_r | rx_valid_r);
endmodule
