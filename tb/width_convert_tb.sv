`timescale 1 ns / 100 ps

module width_convert_tb();


    logic        clk;
    logic        rst;
    logic        wren;
    logic [31:0] din;
    logic        rden;
    logic [ 7:0] dout;
    logic        valid;

    uart_reg24to8 dut (.*);

    initial begin : gen_clk
      clk = 1'b0;
      while (1) #5 clk = ~clk;
    end

    initial begin : gen_stimuli
      rst = 1'b1;

      for (int i = 0; i < 4; i++) @(negedge clk);

      rst = 1'b0;
      din = 32'h0cabcdef;
      wren = 1'b1;

      @(negedge clk);

      wren = 1'b0;
      rden = 1'b1;

      for (int i = 0; i < 5; i++) @(posedge clk);

      $stop;
    end
endmodule
