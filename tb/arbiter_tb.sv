`timescale 1 ns / 100 ps

module arbiter_tb;

    logic [7:0] rx_fifo_empty;
    logic [7:0] rx_fifo_almost_full;

    logic rst;
    logic clk;

    logic read_periph_data;

    logic [2:0] grant;

    arbiter DUT (.*);

    // Generate a clock with a 10 ns period
    always begin : generate_clock
        #5 clk = ~clk;
    end

    initial begin
        $timeformat(-9, 0, " ns");

        //set read_periph_data to true
        read_periph_data <= 1;
        @(posedge clk);

        // Reset the register. Gollowing the advice from the previous example,
        // Reset is asserted with a non-blocking assignment.
        rst <= 1'b1;

        // Wait 5 cycles
        for (int i=0; i < 5; i++)
            @(posedge clk);

        // Clear reset on a falling edge (as suggested in previous example)
        @(negedge clk);
        rst <= 1'b0;
        @(posedge clk);

        //outer loop to test all possible rx_fifo_empty
        //inside run each for 9 cycles to watch it shift
        for (int i = 0; i < 256; i++) begin
            rx_fifo_empty <= i;

            //wait 9 cycles
            repeat (9) @(posedge clk);
        end



        //second test to test all rx_Fifo_almost_full
        //inside randomize rx_fifo_empty - shouldnt impact 

        $display("Tests completed.");
        $stop;
    end

endmodule