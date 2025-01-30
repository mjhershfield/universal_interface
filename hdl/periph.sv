// Static peripheral block - contains the reconfigurable logic and the FIFOs/etc.
import lycan_globals::*;

module periph #(
    parameter logic [periph_address_width-1:0] ADDRESS
) (
    input logic clk,
    input logic rst,

    // I/O pins for the peripheral
    input logic [inputs_per_peripheral-1:0] in,
    output logic [outputs_per_peripheral-1:0] out,
    // For now, only need to tristate a subset of all outputs
    output logic [tristates_per_peripheral-1:0] tristate,

    // FIFO for data being received from the USB bus
    input logic [usb_packet_width-1:0] tx_data,
    input logic tx_valid,
    output logic tx_full,

    // FIFO for data being sent back to the USB bus
    output logic [usb_packet_width-1:0] rx_data,
    input logic rx_read,
    output logic rx_empty,
    output logic rx_almost_full,
    output logic rx_full,

    // Status flags
    output logic idle,
    output logic ready
);

  logic
      tx_fifo_wren,
      tx_fifo_rden,
      tx_fifo_full,
      tx_fifo_empty,
      tx_fifo_wr_rst_busy,
      tx_fifo_rd_rst_busy;

  logic [usb_packet_width-1:0] tx_fifo_din, tx_fifo_dout;
  logic
      rx_fifo_wren,
      rx_fifo_rden,
      rx_fifo_full,
      rx_fifo_empty,
      rx_fifo_almost_full,
      rx_fifo_wr_rst_busy,
      rx_fifo_rd_rst_busy;
  logic [usb_packet_width-periph_address_width-1:0] rx_fifo_din;
  logic [usb_packet_width-1:0] rx_fifo_dout;


  // Connect to FIFOs (top bits of FIFOs are constant address)
  // Instantiate TX FIFO
  periph_local_tx_fifo tx_fifo (
      .clk(clk),
      .rst(rst),
      .din(tx_fifo_din),
      .wr_en(tx_fifo_wren),
      .rd_en(tx_fifo_rden),
      .dout(tx_fifo_dout),
      .full(tx_fifo_full),
      .empty(tx_fifo_empty),
      .wr_rst_busy(tx_fifo_wr_rst_busy),
      .rd_rst_busy(tx_fifo_rd_rst_busy)
  );

  // Instantiate RX FIFO
  periph_local_rx_fifo rx_fifo (
      .clk(clk),
      .rst(rst),
      .din({ADDRESS, rx_fifo_din}),
      .wr_en(rx_fifo_wren),
      .rd_en(rx_fifo_rden),
      .dout(rx_fifo_dout),
      .full(rx_fifo_full),
      .empty(rx_fifo_empty),
      .prog_full(rx_fifo_almost_full),
      .wr_rst_busy(rx_fifo_wr_rst_busy),
      .rd_rst_busy(rx_fifo_rd_rst_busy)
  );

  // Instantiate reconfig_periph_wrapper
  // TODO: need to account for FIFO read latency of 1 cycle
  // TODO: change FIFO widths to 29 bits? (stripping address)

//   assign rx_fifo_din[usb_packet_width-1:usb_packet_width-periph_address_width] = ADDRESS;

  reconfig_periph_wrapper reconfig_periph (
      .clk(clk),
      .rst(rst),
      .in(in),
      .out(out),
      .tristate(tristate),
      .tx_data(tx_fifo_dout[usb_packet_width-periph_address_width-1:0]),
      .tx_empty(tx_fifo_empty),
      .tx_rden(tx_fifo_rden),
      .rx_data(rx_fifo_din),
      .rx_wren(rx_fifo_wren),
      .rx_full(rx_fifo_full),
      .idle(idle)
  );

  // Connect FIFOs to top-level signals
  assign tx_fifo_din = tx_data;
  assign tx_fifo_wren = tx_valid & (tx_data[usb_packet_width-1:usb_packet_width-periph_address_width] == ADDRESS);
  assign tx_full = tx_fifo_full;

  assign rx_data = {ADDRESS, rx_fifo_dout[usb_packet_width-periph_address_width-1:0]};
  assign rx_fifo_rden = rx_read;
  assign rx_empty = rx_fifo_empty;
  assign rx_almost_full = rx_fifo_almost_full;
  assign rx_full = rx_fifo_full;

  // "Ready" counter to enforce 60+ cycle no access zone after reset
  logic [5:0] reset_counter;
  always_ff @(posedge clk or posedge rst) begin
    if (rst == 1'b1) reset_counter <= '0;
    else begin
      if (reset_counter != '1) reset_counter <= reset_counter + 1;
    end
  end

  assign ready = (reset_counter == '1);
endmodule
