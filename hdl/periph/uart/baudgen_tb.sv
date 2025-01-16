`timescale 1 ns / 100 ps
module baudgen_tb;

  // Local signals
  logic clk;
  logic rst;
  logic baud_out;
  logic [1:0] baud_sel;
  
  // generate clock
  initial begin
    clk = 1'b0;
    while (1) #5 clk = ~clk;
  end;

  baudrategen baudgen(
   .baud_out(baud_out),     // output of baud gen
   .clkin(clk),        // input  clock of baud gen (100MHz)
   .rst(rst),          // reset
   .baud_sel(baud_sel)      // 00-19200, 01-38400, 10-57600, 11 - 115200
  );

  assign baud_sel = 2'd3;

  initial begin
    rst <= 1'b1;
    for (int i = 0; i < 5; i++)
      @(posedge clk);
    @(negedge clk);
    rst <= 1'b0;
  end

endmodule
