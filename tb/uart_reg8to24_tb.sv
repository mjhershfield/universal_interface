`timescale 1 ns / 100 ps

module uart_reg8to24_tb();


    logic        clk;
    logic        rst;
    logic        wren;
    logic [7:0] din;
    logic        rden;
    logic [31:0] dout;
    logic   [1:0]     valid_bytes;

    uart_reg8to24 dut (.*);

    initial begin : gen_clk
      clk = 1'b0;
      while (1) #5 clk = ~clk;
    end

    initial begin : gen_stimuli
      rst = 1'b1;

      for (int i = 0; i < 4; i++) @(negedge clk);

      rst = 1'b0;
      din = 8'hab;
      wren = 1'b1;

      @(negedge clk);

      din = 8'h01;

      @(negedge clk);

      din = 8'hef;

      @(negedge clk);

      rden = 1'b1;
      wren = 1'b0;

      @(negedge clk)
      rden = 1'b0;
      wren = 1'b1;

      @(negedge clk);

      din = 8'h01;

      @(negedge clk);

      wren = 1'b0;
      rden = 1'b1;

      @(negedge clk);

      rden = 1'b0;

      for (int i = 0; i < 5; i++) @(posedge clk);

      $stop;
    end
endmodule
