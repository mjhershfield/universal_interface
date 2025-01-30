`timescale 1 ns / 10 ps


module clk_div_tb #(
    parameter int width = 24
    //parameter int NUM_TESTS = 1000
);
    logic clk, rst, div_clk;
    logic [width-1:0] max_count;
    int cycles = 0;
    logic div_clk_prev;


    clk_div #(.width(width)) DUT (
        .clk(clk),
        .rst(rst),
        .div_clk(div_clk),
        .max_count(max_count)
    );

    initial begin : generate_clock
        clk <= 1'b0;
        forever #5 clk <= ~clk;
    end

    initial begin : drive_inputs
        $timeformat(-9, 0, " ns");

        rst <= 1'b1;
        max_count  <= 10;

        repeat (5) @(posedge clk);

        rst <= 1'b0;

        

        div_clk_prev = div_clk;

        for (int i = 0; i < 100; i++) begin
            @(posedge clk);
            if (div_clk != div_clk_prev) begin
                cycles = cycles + 1;
            end
            div_clk_prev = div_clk;
        end

        disable generate_clock;
        $display("Tests completed. Cycles: %0d", cycles);
    end

endmodule