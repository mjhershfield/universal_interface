`timescale 1 ns / 100 ps

module delay_tb;

  localparam WIDTH = 1;
  localparam CYCLES = 1;
  logic clk = 0, rst = 1, en = 1;
  logic [WIDTH-1:0] in, out;
  int num_errors = 0;

  delay #(
      .WIDTH (WIDTH),
      .CYCLES(CYCLES)
  ) delay_1 (
      .*
  );

  always begin : generate_clock
    #5 clk = ~clk;
  end

  initial begin
    @(posedge clk);
    @(posedge clk);

    rst = 0;
    in  = '1;

    for (int i = 0; i < CYCLES; i++) begin
      if (out != '0) begin
        $display("OUTPUT SHOULD BE 0!");
        num_errors += 1;
      end
      @(posedge clk);
    end

    if (out != '1) begin
      $display("OUTPUT SHOULD BE 1!");
      num_errors += 1;
    end
    @(posedge clk);


    $display("Tests completed");
    $stop;
  end

endmodule
