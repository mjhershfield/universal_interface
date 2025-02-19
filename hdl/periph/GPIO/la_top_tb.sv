`timescale 1ns / 1ns

module la_top_tb;
    // Parameters
    parameter width = 32;

    // Testbench Signals
    logic clk;
    logic rst;
    logic [width-1:0] packet_out;
    logic [15:0] pin_vals, pin_vals_prev;
    logic data_valid;

    // Pass/Fail Counters
    int pass_count = 0;
    int fail_count = 0;

    // Instantiate DUT (Device Under Test)
    la_top #(.width(width)) dut (
        .clk(clk),
        .rst(rst),
        .packet_in(32'b0),  // Ignored
        .packet_out(packet_out),
        .pin_vals(pin_vals),
        .data_valid(data_valid)
    );

    // Generate Clock (50 MHz Example)
    always #10 clk = ~clk; // 20ns period -> 50 MHz

    // Test Sequence
    initial begin
        // Initialize signals
        clk = 0;
        rst = 1;
        pin_vals = 16'h0000;
        pin_vals_prev = 16'h0000;

        // Hold reset for a few cycles
        #50 rst = 0;

        // Iterate through all 16-bit values using a for loop
        for (int i = 0; i < 65536; i++) begin
            #320; // Wait 16 clock cycles to match division factor

            pin_vals_prev = pin_vals; // Store previous value for delayed comparison
            pin_vals = i; // Assign new pin values

            #20; // Wait 1 cycle for registered update
            
            // Assertions to Verify Output (accounting for 1-cycle delay)
            if (packet_out[15:0] !== pin_vals_prev ||
                packet_out[27:26] !== 2'b10 ||
                data_valid !== 1'b1) 
            begin
                $error("Mismatch at time %0t: pin_vals_prev=%h, packet_out=%h, data_valid=%b", 
                       $time, pin_vals_prev, packet_out, data_valid);
                fail_count++;
            end else begin
                pass_count++;
            end
        end

        // Print Summary
        $display("\nTest Completed.");
        $display("Total Passes: %0d", pass_count);
        $display("Total Fails: %0d", fail_count);

        // End simulation
        #1000 $finish;
    end
endmodule
