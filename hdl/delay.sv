// Greg Stitt
// University of Florida
//
// This file illustrates how to implement a delay module structurally
// as a sequence of registers. It introduces the unpacked array construct.


// Module: register
// Description: Basic register.

module register #(
    parameter int WIDTH
) (
    input  logic             clk,
    input  logic             rst,
    input  logic             en,
    input  logic [WIDTH-1:0] in,
    output logic [WIDTH-1:0] out
);

  always_ff @(posedge clk or posedge rst)
    if (rst) out <= '0;
    else if (en) out <= in;

endmodule  // register

module delay #(
    parameter int CYCLES,
    parameter int WIDTH
) (
    input  logic             clk,
    rst,
    en,
    input  logic [WIDTH-1:0] in,
    output logic [WIDTH-1:0] out
);

  if (CYCLES < 0) begin : g_cycles_must_be_ge_0
    cycles_parameter_must_be_ge_0();
  end

  if (WIDTH < 1) begin : g_width_must_bt_gt_0
    width_parameter_must_be_gt_0();
  end

  logic [WIDTH-1:0] regs[CYCLES+1];

  if (CYCLES == 0) begin : g_cycles_eq_0
    assign out = in;
  end else if (CYCLES > 0) begin : g_cycles_gt_0
    genvar i;
    for (i = 0; i < CYCLES; i++) begin : g_reg_array
      register #(
          .WIDTH(WIDTH)
      ) reg_array (
          .in (regs[i]),
          .out(regs[i+1]),
          .*
      );
    end

    assign regs[0] = in;

    // The last register's output goes to the delay's output.
    assign out = regs[CYCLES];

  end
endmodule
