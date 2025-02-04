import lycan_globals::*;
import uart_pkg::*;

module uart (
    input logic clk,
    input logic rst,

    input logic [inputs_per_peripheral-1:0] in,
    output logic [outputs_per_peripheral-1:0] out,
    // For now, only need to tristate a subset of all outputs
    output logic [tristates_per_peripheral-1:0] tristate,

    // peripheral address is not stored in the local FIFOs.
    input logic [usb_packet_width-periph_address_width-1:0] tx_data,
    input logic tx_empty,
    output logic tx_rden,

    output logic [usb_packet_width-periph_address_width-1:0] rx_data,
    output logic rx_wren,
    input logic rx_full,

    output logic idle
);

  logic uart_tx_clk, uart_tx_busy, uart_tx_empty, uart_tx_rden;
  logic [7:0] uart_tx_data;
  logic tx_split_wren, tx_split_rden, tx_split_valid;

  uart_tx tx (
      .clk(uart_tx_clk),
      .rst(rst),
      .tx(out[0]),
      .tx_busy(uart_tx_busy),
      .tx_data(uart_tx_data),
      .tx_empty(~tx_split_valid),
      .tx_rden(uart_tx_rden),
      .num_data_bits(4'h8),
      .stop_bits(STOP_BITS_1),
      .parity(PARITY_NONE)
  );

  clk_div clock_divider (
      .clk(clk),
      .rst(rst),
      .div_clk(uart_tx_clk),
      .max_count(24'd434)
  );

  uart_reg24to8 tx_splitter (
      .clk  (clk),
      .rst  (rst),
      .wren (tx_split_wren),
      .din  (tx_data),
      // Need to synchronize to slower clock domain
      .rden (tx_split_rden),
      .dout (uart_tx_data),
      .valid(tx_split_valid)
  );

  handshake tx_split_rden_handshake (
      .clk_wr (uart_tx_clk),
      .rst_wr (rst),
      .clk_rd (clk),
      .rst_rd (rst),
      .start  (uart_tx_rden),
      .read_it(tx_split_rden),
      // too lazy to implement... shouldn't be needed
      // .done()
  );

  assign tx_split_wren = ~tx_split_valid & ~tx_empty;
  assign tx_rden = tx_split_wren;
  assign idle = ~uart_tx_busy;
  assign out[3:1] = '0;

endmodule
