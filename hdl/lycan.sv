
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
  logic read_periph_data;
  (* mark_debug = "true" *) logic [num_peripherals-1:0]
      periph_tx_fulls,
      periph_rx_rdens,
      periph_rx_emptys,
      periph_rx_almost_fulls,
      periph_rx_fulls,
      periph_idles,
      periph_readys;
  // logic fifos_ready;
  logic [inputs_per_peripheral*num_peripherals-1:0] periph_ins;
  logic [outputs_per_peripheral*num_peripherals-1:0] periph_outs;
  logic [tristates_per_peripheral*num_peripherals-1:0] periph_tristates;
  // (* mark_debug = "true" *) logic [usb_packet_width-1:0] periph_tx_din;
  logic [2:0] periph_grant;
    (* mark_debug = "true" *) logic [num_peripherals-1:0] decoded_grant;
  (* mark_debug = "true" *) logic [usb_packet_width-1:0] arbiter_out;
  logic arbiter_out_valid;

  logic [num_peripherals-1:0][usb_packet_width-1:0] mux_options;

  (* mark_debug = "true" *) logic [usb_packet_width-1:0] usb_data_in, usb_data_out;
  (* mark_debug = "true" *) logic usb_data_tri;
  (* mark_debug = "true" *) logic [3:0] be_in, be_out;
  (* mark_debug = "true" *) logic be_tri;
  (* mark_debug = "true" *) logic lycan_rd, lycan_wr;
  (* mark_debug = "true" *) logic [31:0] lycan_in, lycan_out;
  (* mark_debug = "true" *) logic in_fifo_empty, out_fifo_empty;


  // Set voltage regulator for 2.5V
  // TODO: Do we want a separate clock domain to configure set_vadj and vadj_en sequentially after reset?
  // (cannot be the main clock domain since reset disables the FIFO clock and FIFO clock depends on VADJ power)
  assign set_vadj = 2'b10;
  assign vadj_en = 1'b1;

  // The CPU_RST button on our dev board is active-low
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
      .rd_data_valid(periph_tx_valid),
      .usb_data_tri(usb_data_tri),
      .be_in(be_in),
      .be_out(be_out),
      .be_tri(be_tri),
      .periph_data_available(~out_fifo_empty),
      // .read_periph_data(read_periph_data),
      .periph_ready(&periph_readys)
  );

  // Tristate buffer for USB data bus
  genvar usb_bit;
  for (usb_bit = 0; usb_bit < usb_packet_width; usb_bit++) begin : gen_usb_iobuf
    IOBUF usb_iobuf (
        .O (usb_data_in[usb_bit]),
        .IO(usb_data[usb_bit]),
        .I (usb_data_out[usb_bit]),
        .T (usb_data_tri)
    );
  end

  // Tristate buffer for byte enable bus
  genvar be_bit;
  for (be_bit = 0; be_bit < 4; be_bit++) begin : gen_be_iobuf
    IOBUF be_iobuf (
        .O (be_in[be_bit]),
        .IO(usb_be[be_bit]),
        .I (be_out[be_bit]),
        .T (be_tri)
    );
  end

  // Fifo between
  ftdi_fifo ftdi_to_lycan_fifo (
      .clk  (clk),           // input wire clk
      .rst  (rst),           // input wire rst
      .din  (usb_data_in),   // input wire [31 : 0] din
      .wr_en(~usb_rden_l & periph_tx_valid),   // input wire wr_en
      .rd_en(lycan_rd),      // input wire rd_en
      .dout (lycan_in),      // output wire [31 : 0] dout
      // .full       (full),         // output wire full
      .empty(in_fifo_empty)  // output wire empty
      // .wr_rst_busy(wr_rst_busy),  // output wire wr_rst_busy
      // .rd_rst_busy(rd_rst_busy)   // output wire rd_rst_busy
  );

  ftdi_fifo lycan_to_ftdi_fifo (
      .clk  (clk),            // input wire clk
      .rst  (rst),            // input wire rst
    // switch to arbiter_out in the future
      .din  (lycan_out),      // input wire [31 : 0] din
      .wr_en(lycan_wr),       // input wire wr_en
      .rd_en(~usb_wren_l),    // input wire rd_en
      .dout (usb_data_out),   // output wire [31 : 0] dout
      // .full       (full),         // output wire full
      .empty(out_fifo_empty)  // output wire empty
      // .wr_rst_busy(wr_rst_busy),  // output wire wr_rst_busy
      // .rd_rst_busy(rd_rst_busy)   // output wire rd_rst_busy
  );

  assign lycan_out = arbiter_out;
  assign lycan_wr  = arbiter_out_valid;
  assign lycan_rd  = ~in_fifo_empty;

  arbiter periph_arbiter (
      .clk(clk),
      .rst(rst),
      .rx_fifo_empty(periph_rx_emptys),
      .rx_fifo_almost_full(periph_rx_almost_fulls),
      // .read_periph_data(read_periph_data),
      .grant(periph_grant)
  );

  // MUX to select peripheral with bus control
  mux #(
      .NUM_INPUTS  (num_peripherals),
      .WIDTH_INPUTS(usb_packet_width)
  ) arbiter_mux (
      .in (mux_options),
      .sel(periph_grant),
      .out(arbiter_out)
  );

  // MUX to output if current peripheral granted bus access has valid data
  mux #(
      .NUM_INPUTS  (num_peripherals),
      .WIDTH_INPUTS(1)
  ) valid_mux (
      .in (periph_rx_rdens),
      .sel(periph_grant),
      .out(arbiter_out_valid)
  );

  // Instantiate 8 loopback peripherals
  genvar periph_num;
  for (periph_num = 0; periph_num < num_peripherals; periph_num++) begin : gen_peripherals
    periph #(
        .ADDRESS(3'(periph_num))
    ) loopback (
        .clk(clk),
        .rst(rst),
        .in(periph_ins[periph_num*inputs_per_peripheral+:inputs_per_peripheral]),
        .out(periph_outs[periph_num*outputs_per_peripheral+:outputs_per_peripheral]),
        .tristate(periph_tristates[periph_num*tristates_per_peripheral+:tristates_per_peripheral]),
        .tx_data(lycan_in),
        .tx_valid(~in_fifo_empty),
        .tx_full(periph_tx_fulls[periph_num]),
        .rx_data(mux_options[periph_num]),
        .rx_read(periph_rx_rdens[periph_num]),
        .rx_empty(periph_rx_emptys[periph_num]),
        .rx_almost_full(periph_rx_almost_fulls[periph_num]),
        .rx_full(periph_rx_fulls[periph_num]),
        .idle(periph_idles[periph_num]),
        .ready(periph_readys[periph_num])
    );
  end

  // Decode grant signal to periph_rdens vector
  decoder #(
      .WIDTH(8)
  ) periph_rden_decoder (
      .in(periph_grant),
      .valid(1'b1),
      .out(decoded_grant)
  );

  // Register all outputs to the FTDI
  // delay #(.WIDTH(32+1+4+1+4), .CYCLES(1)) ftdi_outputs_delay (
  //   .clk(clk),
  //   .rst(rst),
  //   .en(1'b1),
  //   .in({usb_data_out, usb_data_tri, be_out, be_tri, controller_wren, controller_rden, controller_outen, controller_rst}),
  //   .out({usb_data_out_r, usb_data_tri_r, be_out_r, be_tri_r, usb_wren_l, usb_rden_l, usb_outen_l, usb_rst_l})
  // );

  // assign usb_data_out_r = usb_data_out;
  // assign usb_data_tri_r = usb_data_tri;
  // assign be_out_r = be_out;
  // assign be_tri_r = be_tri;
  // assign usb_wren_l = controller_wren;
  // assign usb_rden_l = controller_rden;
  // assign usb_outen_l = controller_outen;
  // assign usb_rst_l = controller_rst;

  assign periph_rx_rdens = decoded_grant & ~periph_rx_emptys;

endmodule
