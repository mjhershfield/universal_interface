`timescale 1 ns / 100 ps

module mock_fifo #(
    parameter int WIDTH = 32,
    parameter int INITIAL_FILLED = 1
) (
    input logic clk,
    input logic rst,
    input logic delay,
    input logic rden,
    input logic outen,
    output logic [WIDTH-1:0] dout,
    output logic empty
);
  int remaining_data_amt;
  logic [WIDTH-1:0] dout_r;

  always @(posedge clk or posedge rst) begin
    if (rst) begin
      dout_r[29:0] <= $urandom;
      remaining_data_amt <= INITIAL_FILLED;
    end else begin
      if (rden) begin
        if (remaining_data_amt > 0) begin
          remaining_data_amt <= remaining_data_amt - 1;
          dout_r[29:0] = $urandom;
        end else begin
          dout_r[29:0] <= 0;
        end
      end
    end
  end

  assign dout_r[31:30] = 2'b0;

  assign dout = (outen) ? dout_r : 'z;

  assign empty = (delay) ? '1 : remaining_data_amt == 0;

endmodule

module lycan_tb;
  parameter int WIDTH = 32;

  logic clk = 0;
  logic rst;
  logic rden;
  logic delay;
  wire [31:0] dout;
  logic outen;
  logic empty;

  // LYCAN PINS
  logic rst_l;
  wire [31:0] usb_data;
  wire [3:0] usb_be;
  logic usb_tx_full;  // 0 = space available; 1 = full
  logic usb_rx_empty;  // 0 = data available; 1 = empty
  logic usb_siwu;  // TODO: constant pullup. can this be done in constraints?
  logic usb_wren_l;
  logic usb_rden_l;
  logic usb_outen_l;
  logic usb_rst_l;
  logic usb_wakeup;  // bidirectional. as input; 0 = USB active; 1 = usb suspended.
  logic [1:0] usb_gpio;  // TWO CONFIGURABLE GPIO. WHAT DO THEY DO?
  wire [width_dut_pins-1:0] dut_pins;  // DUT pins
  // Power supplies on Nexys Video
  logic [1:0] set_vadj;
  logic vadj_en;

  assign rst_l = ~rst;
  assign rden = ~usb_rden_l;
  assign usb_rx_empty = empty;
  assign outen = ~usb_outen_l;
  assign usb_tx_full = '0;

  mock_fifo #(
      .WIDTH(WIDTH),
      .INITIAL_FILLED(5)
  ) fdti_input (
      .dout(usb_data),
      .*
  );
  lycan DUT (.*);

  always begin : generate_clk
    clk <= ~clk;
    #5;
  end

  initial begin
    rst   = 1;
    delay = 0;

    for (int i = 0; i < 5; i++) @(posedge clk);

    @(negedge clk);

    rst = 0;

    // for (int i = 0; i < 40; i++)
    //     @(posedge clk);

    // @(negedge clk);

    // delay = 0;
  end

endmodule
