import lycan_globals::*;
//import uart_pkg::*;

module spim (
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

  localparam int CLK_RATIO = 4999;
  // localparam int CLK_RATIO = 8;
  localparam logic [31:0] READ_TIMEOUT = 32'(CLK_RATIO * 10 * 100);

  logic spi_tx_clk, spi_tx_busy, spi_tx_rden;
  logic [7:0] spi_tx_data;
  logic tx_split_wren, tx_split_rden, tx_split_valid;
  logic spi_rx_clk, spi_rx_busy, spi_rx_full, spi_rx_error, spi_rx_done;
  logic [7:0] spi_rx_data;
  logic rx_comb_wren, rx_comb_rden;
  logic [23:0] rx_comb_dout;
  logic [ 1:0] rx_comb_valid_bytes;

  logic [31:0] rx_cycle_counter_r;
  logic force_read;

  spi_master master (
    .clk(spi_tx_clk),
    .rst(rst),
    .tx_data(spi_tx_data),
    .tx_empty(~tx_split_valid),
    .CS_L(out[0]), 
    .SCLK(out[1]), 
    .MOSI(out[2]), 
    .MISO(in[0]),
    .tx_rden(spi_tx_rden),
    .rx_data(spi_rx_data),
    .rx_valid(spi_rx_done) //??
  );

  clk_div clk_div_spi(
    .clk(clk),
    .rst(rst),
    .div_clk(spi_tx_clk),
    .max_count(24'(CLK_RATIO))
);

  uart_reg24to8 tx_splitter (
      .clk  (clk),
      .rst  (rst),
      .wren (tx_split_wren),
      .din  (tx_data),
      // Need to synchronize to slower clock domain
      .rden (tx_split_rden),
      .dout (spi_tx_data),
      .valid(tx_split_valid)
  );

  handshake tx_split_rden_handshake (
      .clk_wr (spi_tx_clk),
      .rst_wr (rst),
      .clk_rd (clk),
      .rst_rd (rst),
      .start  (spi_tx_rden),
      .read_it(tx_split_rden)
      // too lazy to implement... shouldn't be needed
      // .done()
  );

  uart_reg8to24 rx_combiner (
      .clk(clk),
      .rst(rst),
      .wren(rx_comb_wren),
      .din(spi_rx_data),
      .rden(rx_comb_rden),
      .dout(rx_comb_dout),
      .valid_bytes(rx_comb_valid_bytes)
  );

  handshake rx_comb_wren_handshake (
      .clk_wr (spi_tx_clk),
      .rst_wr (rst),
      .clk_rd (clk),
      .rst_rd (rst),
      .start  (spi_rx_done),
      .read_it(rx_comb_wren)
      // too lazy to implement... shouldn't be needed
      // .done()
  );

  // TODO: trigger a read from the combiner if nothing has been received for a long time.
  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      rx_cycle_counter_r <= READ_TIMEOUT;
    end else begin
      if (rx_cycle_counter_r == '0 || rx_comb_valid_bytes == 2'd3) begin
        rx_cycle_counter_r <= READ_TIMEOUT;
      end else if (rx_comb_valid_bytes != 2'b0) begin
        rx_cycle_counter_r <= rx_cycle_counter_r - 1;
      end
    end
  end
  assign force_read = (rx_cycle_counter_r == '0);

  assign spi_comb_wren = spi_rx_done;
  assign rx_data = {1'b0, rx_comb_valid_bytes, 2'b0, rx_comb_dout};

  assign tx_split_wren = ~tx_split_valid & ~tx_empty;
  assign tx_rden = tx_split_wren;
  assign rx_comb_rden = (rx_comb_valid_bytes == 2'd3) | force_read;
  assign rx_wren = rx_comb_rden;

  // General signals
  assign idle = ~(spi_tx_busy | spi_rx_busy);
endmodule
