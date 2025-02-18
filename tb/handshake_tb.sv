`timescale 1 ns / 100 ps

module handshake_tb;

  logic clk_wr, rst_wr, clk_rd, rst_rd, start, read_it, done;

  handshake DUT (.*);

  always begin : generate_wr_clock
    clk_wr = 1'b0;
    while (1) #5 clk_wr = ~clk_wr;
  end

  always begin : generate_rd_clock
    clk_rd = 1'b0;
    while (1) #20 clk_rd = ~clk_rd;
  end

  initial begin
    rst_wr = 1'b1;
    rst_rd = 1'b1;
    start = 1'b0;

    @(posedge clk_rd);
    @(negedge clk_rd);

    rst_rd = 1'b0;
    rst_wr = 1'b0;

    @(posedge clk_wr);

    start = 1'b1;

    @(posedge clk_wr);

    start = 1'b0;

    @(negedge done);
    @(posedge clk_wr);

    start = 1'b1;

    @(posedge clk_wr);

    start = 1'b0;

    @(negedge done);

    $stop;
  end

endmodule
