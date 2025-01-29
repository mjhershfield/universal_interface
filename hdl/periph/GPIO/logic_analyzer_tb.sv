`timescale 1 ns / 100 ps

module logic_analyzer_tb #(parameter int width = 16);

    logic clk, rst;
    logic [width-1:0] pin_vals, reads;

    int successes = 0;
    int fails = 0;

    logic_analyzer #(.width(width)) DUT (
        .clk(clk),
        .rst(rst),
        .reads(reads),
        .pin_vals(pin_vals)
    );

    initial begin : generate_clock
        clk <= 1'b0;
        forever #5 clk <= ~clk;
    end

    initial begin : drive_inputs
        $timeformat(-9, 0, " ns");

        rst <= 1'b1;
        pin_vals  <= '1;

        repeat (5) @(posedge clk);

        rst <= 1'b0;
        

    while (pin_vals != '0) begin //gives one failue when coming off reset but thats just the tb
        @(posedge clk);
        if ((reads - 1) == pin_vals) begin
            successes++;
        end else begin
            fails++;
            $display("Failure detected at time: %t", $time);
        end
        pin_vals--;
    end


        disable generate_clock;
        $display("Tests completed. fails: %0d successes: %0d", fails, successes);
    end
    

    
endmodule