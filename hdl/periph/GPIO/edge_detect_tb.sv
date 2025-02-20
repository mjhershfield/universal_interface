`timescale 1ns / 1ps

module edge_detect_tb;
    logic clk;
    logic rst;
    logic signal_in;
    logic posedge_detected;

    // Instantiate the Device Under Test (DUT)
    edge_detect dut (
        .clk(clk),
        .rst(rst),
        .signal_in(signal_in),
        .posedge_detected(posedge_detected)
    );

    // Generate clock (50 MHz -> 20 ns period)
    always #10 clk = ~clk;

    // Test Sequence
    initial begin
        // Initialize signals
        clk = 0;
        rst = 1;
        signal_in = 0;

        // Reset for a few cycles
        #50 rst = 0;

        // Apply test patterns
        #15 signal_in = 1; // Rising edge should be detected
        #20 signal_in = 0; // Falling edge (should NOT be detected)
        #20 signal_in = 1; // Another rising edge should be detected
        #40 signal_in = 0; // Falling edge again

        // Wait some cycles
        #100;

        // End simulation
        $finish;
    end

    // Monitor output
    always @(posedge clk) begin
        if (posedge_detected) begin
            $display("Rising edge detected at time %0t. signal_in = %b", $time, signal_in);
        end
    end
endmodule
