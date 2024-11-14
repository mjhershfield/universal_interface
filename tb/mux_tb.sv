module mux_tb;
  localparam int NUM_INPUTS = 8;
  localparam int WIDTH_INPUTS = 4;

  logic [NUM_INPUTS-1:0][WIDTH_INPUTS-1:0] in;
  logic [$clog2(NUM_INPUTS)-1:0] sel;
  logic [WIDTH_INPUTS-1:0] out;

  mux #(
      .NUM_INPUTS  (NUM_INPUTS),
      .WIDTH_INPUTS(WIDTH_INPUTS)
  ) DUT (
      .*
  );

  initial begin
    logic [WIDTH_INPUTS-1:0] correct_out;
    $timeformat(-9, 0, " ns");

    // Set each input to a different number
    for (int i = 0; i < NUM_INPUTS; i++) begin
      in[i][WIDTH_INPUTS-1:0] = i;
    end

    for (int s = 0; s < NUM_INPUTS; s++) begin
      sel = s;

      #10;

      if (out != s) begin
        $display("ERROR: INCORRECT VALUE FOR SELECT NUMBER %d", s);
      end
    end

    $display("Tests completed.");
  end
endmodule
