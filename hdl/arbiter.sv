module arbiter (
    input logic clk,
    input logic rst,

    // Control signals from local peripheral FIFOs
    input logic [7:0] rx_fifo_empty,
    input logic [7:0] rx_fifo_almost_full,

    // If data is being currently read from the peripheral into the FT601
    input logic read_periph_data,

    // Number of peripheral that has control of the bus
    output logic [2:0] grant
);

  logic [2:0] curr_grant = 0;
  logic [7:0] barrel_sh_out;
  logic [2:0] next_grant;

  logic [7:0] rx_request = ~rx_fifo_empty;  // make active high request

  // Logic to modify request signal if any FIFOs are almost full
  always_comb begin
    if (rx_fifo_almost_full > 0) rx_request = rx_fifo_almost_full;
    else rx_request = ~rx_fifo_empty;
  end

  always_ff @(posedge clk) begin
    if (rst) curr_grant <= 0;
    else if (read_periph_data) curr_grant <= next_grant + curr_grant;
    else curr_grant <= curr_grant;
  end

  // Structural
  barrel_shifter BAR_SH_1 (
      .in(rx_request),
      .sh_amt(curr_grant),
      .out(barrel_sh_out)
  );
  priority_encoder PRI_EN_1 (
      .data(barrel_sh_out),
      .y(next_grant)
  );

  assign grant = curr_grant;

endmodule
