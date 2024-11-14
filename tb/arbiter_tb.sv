`timescale 1 ns / 100 ps

module arbiter_tb;

  localparam int NUM_TESTS = 1000;

  logic rst;
  logic clk;

  //main inputs
  logic [7:0] rx_fifo_empty;
  logic [7:0] rx_fifo_almost_full;
  logic read_periph_data;

  //output
  logic [2:0] grant;

  //for tb
  int num_cycles;

  arbiter DUT (.*);

  // Generate a clock
  initial begin : generate_clock
    clk = 1'b0;
    while (1) #5 clk = ~clk;
  end

  initial begin
    $timeformat(-9, 0, " ns");

    // Reset the circuit.
    rst <= 1'b1;
    read_periph_data <= 1'b0;
    rx_fifo_empty <= 8'b0;
    rx_fifo_almost_full <= 8'b0;
    for (int i = 0; i < 5; i++) @(posedge clk);
    @(negedge clk);
    rst <= 1'b0;
    @(posedge clk);

    // Run the tests
    for (int t = 0; t < NUM_TESTS; t++) begin
      rx_fifo_empty <= $random;
      if (t < 3) begin
        rx_fifo_almost_full <= 0;
      end else begin
        rx_fifo_almost_full <= $random;
      end
      read_periph_data <= $random;

      //wait a random number of cycles to check round robin
      num_cycles = $urandom_range(1, 12);
      for (int j = 0; j < num_cycles; j++) @(posedge clk);
    end

    $display("Tests completed.");
    disable generate_clock;
  end

  //compute grant and compare to what it should be
  function automatic logic is_out_correct(logic [7:0] rx_fifo_not_empty, logic read_periph_data,
                                          logic [7:0] rx_fifo_almost_full, logic [2:0] grant,
                                          logic [2:0] prior);

    //check that the current grant is the next highest bit position equivalent value after last grant
    if (read_periph_data == 1) begin
      if (rx_fifo_almost_full > 1) begin
        //rx_fifo_almost_full for full priority round robin


        //FIX LOGIC TO GRANT MSB TO LSB

        //base check
        for (int i = prior + 1; i <= 7; i++) begin
          if (rx_fifo_almost_full[i] == 1) begin
            // i is now desired current grant
            return grant == i;
          end
        end
        //if it didnt return, we never found a 1, continue check from 0 bit
        for (int i = 0; i < prior; i++) begin
          if (rx_fifo_almost_full[i] == 1) begin
            // i is now desired current grant
            return grant == i;
          end
        end
        //at this point keep grant at current
        return grant == prior;
      end else begin
        //rx_fifo_empty for normal round robin
        //rx_fifo_almost_full for full priority round robin

        //base check
        for (int i = prior + 1; i <= 7; i++) begin
          if (rx_fifo_not_empty[i] == 1) begin
            // i is now desired current grant
            return grant == i;
          end
        end
        //if it didnt return, we never found a 1, continue check from 0 bit
        for (int i = 0; i < prior; i++) begin
          if (rx_fifo_not_empty[i] == 1) begin
            // i is now desired current grant
            return grant == i;
          end
        end
        //at this point keep grant at current
        return grant == prior;
      end
      //if we are not reading the grant should not change
    end else begin
      //assert property(@(posedge clk) grant == $past(grant, 1));
      return grant == prior;
    end

  endfunction

  assert property (@(posedge clk) is_out_correct(
      ~rx_fifo_empty, read_periph_data, rx_fifo_almost_full, grant, $past(grant, 1)
  ));

  //needs
  //if we are reading
  //check that the current grant is the next highest bit position equivalent value after last grant
  //look at what the last grant was numerically, convert to a bit position
  //if that bit position is the next bit to MSB of current grant its good
  //or restart from 0 if reach the end
  //if we are not reading
  //check that current grant does not change
  //need to check resets


endmodule
