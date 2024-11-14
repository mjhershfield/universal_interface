import lycan_globals::*;

module lycan (
    input logic clk,   // CLK provided by FT601
    input logic rst_l,

    // FTDI FT601 control signals
    inout logic [31:0] usb_data,
    inout logic [3:0] usb_be,
    (* mark_debug = "true" *) input logic usb_tx_full,  // 0 = space available, 1 = full
    (* mark_debug = "true" *) input logic usb_rx_empty,  // 0 = data available, 1 = empty
    input logic usb_siwu,  // TODO: constant pullup. can this be done in constraints?
    (* mark_debug = "true" *) output logic usb_wren_l,
    (* mark_debug = "true" *) output logic usb_rden_l,
    (* mark_debug = "true" *) output logic usb_outen_l,
    (* mark_debug = "true" *) output logic usb_rst_l,
    input logic usb_wakeup,  // bidirectional. as input, 0 = USB active, 1 = usb suspended.
    // as output, Drive low to send remote wakeup
    input logic [1:0] usb_gpio,  // TWO CONFIGURABLE GPIO. WHAT DO THEY DO?

    inout logic [width_dut_pins-1:0] dut_pins,  // DUT pins

    // Power supplies on Nexys Video
    output logic [1:0] set_vadj,
    output logic vadj_en
);

  // Local signals
  logic rst;
  logic periph_data_available;
  logic read_periph_data;
  logic
      periph_tx_wren,
      periph_tx_full,
      periph_rx_rden,
      periph_rx_empty,
      periph_rx_almost_full,
      periph_rx_full,
      periph_idle,
      periph_ready;
  logic [inputs_per_peripheral-1:0] periph_in;
  logic [outputs_per_peripheral-1:0] periph_out;
  logic [tristates_per_peripheral-1:0] periph_tristate;
  (* mark_debug = "true" *) logic [usb_packet_width-1:0] periph_tx_din, periph_rx_dout;
  logic [2:0] periph_grant;
  logic [usb_packet_width-1:0] arbiter_out;

  logic [num_peripherals-1:0][usb_packet_width-1:0] mux_options;
  logic [3:0] ft601_o_valid;

  // Set voltage regulator for 2.5V
  // TODO: Do we want a separate clock domain to configure set_vadj and vadj_en sequentially after reset?
  // (cannot be the main clock domain since reset disables the FIFO clock and FIFO clock depends on VADJ power)
  assign set_vadj = 2'b10;
  assign vadj_en  = 1'b1;

  // TODO: replace bandaid fix once we have more than one peripheral
  assign periph_tx_wren = |ft601_o_valid;

  always_comb begin
    mux_options = '{default: '0};
    mux_options[0] = periph_rx_dout;
  end

  assign rst = ~rst_l;

  // Instantiate FT601 controller
  ft601_controller ft601 (
      .clk(clk),
      .rst(rst),
      .usb_tx_full(usb_tx_full),
      .usb_rx_empty(usb_rx_empty),
      .usb_wren_l(usb_wren_l),
      .usb_rden_l(usb_rden_l),
      .usb_outen_l(usb_outen_l),
      .usb_rst_l(usb_rst_l),
      .data_o(periph_tx_din),
      .o_valid(ft601_o_valid),
      .data_i(arbiter_out),
      // Could be a bad assumption?
      .i_valid({4{periph_data_available}}),
      .data(usb_data),
      .be(usb_be),
      .periph_data_available(periph_data_available),
      .read_periph_data(read_periph_data),
      .periph_ready(periph_ready)
  );

  // Instantiate peripheral bus arbiter
  arbiter periph_arbiter (
      .clk(clk),
      .rst(rst),
      .rx_fifo_empty({7'h7F, periph_rx_empty}),
      .rx_fifo_almost_full({7'h0, periph_rx_almost_full}),
      .read_periph_data(read_periph_data),
      .grant(periph_grant)
  );

  //   // Register grant output for use with muxing back
  //   delay #(
  //       .WIDTH (3),
  //       .CYCLES(1)
  //   ) grant_mux_delay (
  //       .clk(clk),
  //       .rst(rst),
  //       .en (1'b1),
  //       .in (periph_grant),
  //       .out(periph_grant_r)
  //   );

  //   // Register periph_data available so that i_valid on the ftdi controller is accurate
  //   delay #(
  //       .WIDTH (1),
  //       .CYCLES(1)
  //   ) periph_data_available_delay (
  //       .clk(clk),
  //       .rst(rst),
  //       .en (1'b1),
  //       .in (periph_data_available),
  //       .out(periph_data_available_r)
  //   );

  // MUX to select peripheral with bus control
  mux #(
      .NUM_INPUTS  (num_peripherals),
      .WIDTH_INPUTS(usb_packet_width)
  ) arbiter_mux (
      .in (mux_options),
      .sel(periph_grant),
      .out(arbiter_out)
  );

  // Generate periph_data_available
  assign periph_data_available = ~periph_rx_empty;

  // Instantiate single loopback peripheral
  periph #(
      .ADDRESS(3'b0)
  ) loopback (
      .clk(clk),
      .rst(rst),
      .in(periph_in),
      .out(periph_out),
      .tristate(periph_tristate),
      .tx_data(periph_tx_din),
      .tx_valid(~usb_rden_l),
      .tx_full(periph_tx_full),
      .rx_data(periph_rx_dout),
      .rx_read(periph_rx_rden),
      .rx_empty(periph_rx_empty),
      .rx_almost_full(periph_rx_almost_full),
      .rx_full(periph_rx_full),
      .idle(periph_idle),
      .ready(periph_ready)
  );

  // Calculate periph_data_available and decode read_periph_data
  assign periph_data_available = ~periph_rx_empty;
  assign periph_rx_rden = read_periph_data;

endmodule
