import lycan_globals::*;
import uart_pkg::*;
import config_reg_pkg::*; //contains the mapping of what cfg reg holds what for each peripheral type

module uart (
    input logic clk,
    input logic rst,

    input logic [inputs_per_peripheral-1:0] in,
    output logic [outputs_per_peripheral-1:0] out,
    // For now, only need to tristate a subset of all outputs
    output logic [tristates_per_peripheral-1:0] tristate,

    // peripheral address is not stored in the local FIFOs.
    (* mark_debug = "true" *) input logic [usb_packet_width-periph_address_width-1:0] tx_data,
    (* mark_debug = "true" *) input logic tx_empty,
    (* mark_debug = "true" *) output logic tx_rden,

    (* mark_debug = "true" *) output logic [usb_packet_width-periph_address_width-1:0] rx_data,
    (* mark_debug = "true" *) output logic rx_wren,
    (* mark_debug = "true" *) input logic rx_full,

    output logic idle
);

  localparam int CLK_RATIO = 5208;
  // localparam int CLK_RATIO = 1;
  localparam logic [31:0] READ_TIMEOUT = 32'(CLK_RATIO * 10 * 100);

  logic uart_tx_clk, uart_tx_busy, uart_tx_rden;
  (* mark_debug = "true" *) logic [7:0] uart_tx_data;
  (* mark_debug = "true" *) logic tx_split_wren, tx_split_rden, tx_split_valid;
  logic uart_rx_clk, uart_rx_busy, uart_rx_full, uart_rx_error, uart_rx_done;
  logic [7:0] uart_rx_data;
  (* mark_debug = "true" *) logic rx_comb_wren, rx_comb_rden;
  (* mark_debug = "true" *) logic [23:0] rx_comb_dout;
  (* mark_debug = "true" *) logic [ 1:0] rx_comb_valid_bytes;

  logic [31:0] rx_cycle_counter_r;
  logic force_read;

  logic [31:0] tx_splitter_data;
  logic [31:0] uart_config_data;

  (* mark_debug = "true" *) logic [23:0] uart_cfg_read_data;
  (* mark_debug = "true" *) logic uart_cfg_valid;
  logic [23:0] all_uart_cfg_regs [8];

  (* mark_debug = "true" *) logic [31:0] uart_data_to_split, config_data;

  (* mark_debug = "true" *) logic cfg_read_en, cfg_write_en;

  uart_tx tx (
      .clk(uart_tx_clk),
      .rst(rst),
      .tx(out[0]),
      .tx_busy(uart_tx_busy),
      .tx_data(uart_tx_data),
      .tx_empty(~tx_split_valid),
      .tx_rden(uart_tx_rden),
      .num_data_bits(all_uart_cfg_regs[NUM_DATA_BITS][3:0]), //4'h8
      .stop_bits(stop_bits_t'(all_uart_cfg_regs[STOP_BITS][0])),  //STOP_BITS_1
      .parity(parity_t'(all_uart_cfg_regs[PARITY][1:0]))  //PARITY_NONE
  );

  clk_div tx_clock_divider (
      .clk(clk),
      .rst(rst),
      .div_clk(uart_tx_clk),
      .max_count(24'(CLK_RATIO))
  );

  cfg_packet_check cfg_check (
    .tx_data(tx_data),
    .tx_splitter_data(uart_data_to_split),
    .uart_config_data(config_data)
  );

  always_comb begin

    cfg_read_en = ((tx_data[28] == 1) && (tx_data[27] == 0) && tx_rden);
    cfg_write_en = ((tx_data[28] == 1) && (tx_data[27] == 1) && tx_rden);

  end

  generic_config_regs #(
    .reset_vals({PERIPH_UART, 4'd8, STOP_BITS_1, PARITY_NONE, 3'd4, 1'b0, 1'b0, 1'b0})
    //.reset_vals({4'd1, 4'd2, 4'd3, 4'd4, 4'd5, 4'd6, 4'd7, 4'd8})

  )
  uart_config_regs (
      .clk(clk),
      .rst(rst),
      .packet(config_data),
      .cfg_read_en(cfg_read_en),
      .cfg_write_en(cfg_write_en),
      .read_data(uart_cfg_read_data),
      .valid(uart_cfg_valid),
      .all_regs(all_uart_cfg_regs)
  );

  uart_reg24to8 tx_splitter (
      .clk  (clk),
      .rst  (rst),
      .wren (tx_split_wren),
      .din  (uart_data_to_split),
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
      .read_it(tx_split_rden)
      // too lazy to implement... shouldn't be needed
      // .done()
  );

  clk_div rx_clock_divider (
      .clk(clk),
      .rst(rst),
      .div_clk(uart_rx_clk),
      .max_count(24'(CLK_RATIO / 8))
  );
  
  uart_rx rx (
      .clk(uart_rx_clk),
      .rst(rst),
      .rx(in[0]),
      .rx_busy(uart_rx_busy),
      .rx_data(uart_rx_data),
      // .rx_full(uart_rx_full), // not implemented in uart rx periph
      // .rx_error(uart_rx_error),
      .rx_done(uart_rx_done),
      .num_data_bits(all_uart_cfg_regs[NUM_DATA_BITS][3:0]), //4'h8
      .stop_bits(stop_bits_t'(all_uart_cfg_regs[STOP_BITS][0])),  //STOP_BITS_1
      .parity(parity_t'(all_uart_cfg_regs[PARITY][1:0]))  //PARITY_NONE
  );

  uart_reg8to24 rx_combiner (
      .clk(clk),
      .rst(rst),
      .wren(rx_comb_wren),
      .din(uart_rx_data),
      .rden(rx_comb_rden),
      .dout(rx_comb_dout),
      .valid_bytes(rx_comb_valid_bytes)
  );

  handshake rx_comb_wren_handshake (
      .clk_wr (uart_rx_clk),
      .rst_wr (rst),
      .clk_rd (clk),
      .rst_rd (rst),
      .start  (uart_rx_done),
      .read_it(rx_comb_wren)
      // too lazy to implement... shouldn't be needed
      // .done()
  );

  // TODO: trigger a read from the combiner if nothing has been received for a long time.
  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      rx_cycle_counter_r <= READ_TIMEOUT;
    end else begin
      if ((rx_cycle_counter_r == '0 || rx_comb_valid_bytes == 2'd3) && ~uart_cfg_valid) begin
        rx_cycle_counter_r <= READ_TIMEOUT;
      end else if (rx_comb_valid_bytes != 2'b0) begin
        rx_cycle_counter_r <= rx_cycle_counter_r - 1;
      end
    end
  end
  //edge case where this will miss a trigger due to uart_valid but clock speed difference should mitiage
  assign force_read = (rx_cycle_counter_r == '0 && ~uart_cfg_valid);

  assign uart_comb_wren = uart_rx_done;

  always_comb begin
      //if (tx_split_valid && ~uart_cfg_valid) rx_data = {1'b0, rx_comb_valid_bytes, 2'b00, rx_comb_dout}; //ISSUE
    //need to make sure that reading a config packet wouldnt also somehow set rx_comb_valid_bytes to nonzero
      if (rx_comb_valid_bytes != 2'b00 && ~uart_cfg_valid) rx_data = {1'b0, rx_comb_valid_bytes, 2'b00, rx_comb_dout}; //ISSUE
      else rx_data = {5'b11100, uart_cfg_read_data};
  end

  assign tx_split_wren = ~tx_split_valid & ~tx_empty & ~tx_data[28];
  assign tx_rden = tx_split_wren || (tx_data[28] && ~tx_empty);  //or config
  assign rx_comb_rden = (rx_comb_valid_bytes == 2'd3) | force_read;
  assign rx_wren = rx_comb_rden || uart_cfg_valid;

  // General signals
  assign idle = ~(uart_tx_busy | uart_rx_busy);
  assign out[3:1] = '0;

endmodule
